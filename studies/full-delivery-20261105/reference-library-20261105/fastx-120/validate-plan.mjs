import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const base=path.dirname(fileURLToPath(import.meta.url));
const readJson=name=>JSON.parse(fs.readFileSync(path.join(base,name),'utf8').replace(/^\uFEFF/,''));
const plan=readJson('plan.json'),music=readJson('music-design.json'),scout=readJson('evidence/scout-index.json');
const midiName=plan.rhythm.midi,buf=fs.readFileSync(path.join(base,midiName));
function fail(message){throw new Error(message);}
if(buf.toString('ascii',0,4)!=='MThd')fail('Not MIDI');
const headerLength=buf.readUInt32BE(4),format=buf.readUInt16BE(8),trackCount=buf.readUInt16BE(10),division=buf.readUInt16BE(12);
if(division&0x8000)fail('SMPTE division unsupported by this PPQ validator');
let off=8+headerLength;const tracks=[],tempos=[],timeSignatures=[];
for(let tr=0;tr<trackCount;tr++){
 if(buf.toString('ascii',off,off+4)!=='MTrk')fail('Missing track chunk');
 const len=buf.readUInt32BE(off+4),end=off+8+len;
 let p=off+8,tick=0,running=0,noteOn=0,noteOff=0,lastNoteOff=0,name='',endOfTrackTick=null;
 function vlq(){let value=0,n=0,b;do{if(p>=end||n++>=4)fail('Invalid VLQ');b=buf[p++];value=(value<<7)|(b&127);}while(b&128);return value;}
 while(p<end){
  tick+=vlq();let status=buf[p];if(status&128){p++;if(status<0xf0)running=status;}else{if(!running)fail('Running status missing');status=running;}
  if(status===0xff){
   const type=buf[p++],n=vlq(),data=buf.subarray(p,p+n);p+=n;
   if(type===0x51){if(n!==3)fail('Tempo size');tempos.push({tick,microsecondsPerQuarter:data.readUIntBE(0,3),track:tr});}
   if(type===0x58&&n>=4)timeSignatures.push({tick,numerator:data[0],denominator:2**data[1]});
   if(type===0x03)name=data.toString('utf8');
   if(type===0x2f)endOfTrackTick=tick;
  }else if(status===0xf0||status===0xf7){p+=vlq();running=0;}
  else if(status>=0x80&&status<0xf0){
   const kind=status&0xf0,n=kind===0xc0||kind===0xd0?1:2;
   if(p+n>end)fail('Truncated MIDI channel event');
   const data=buf.subarray(p,p+n);p+=n;
   if(kind===0x90&&data[1]>0)noteOn++;
   if(kind===0x80||(kind===0x90&&data[1]===0)){noteOff++;lastNoteOff=Math.max(lastNoteOff,tick);}
  }else fail(`Unsupported system status ${status}`);
 }
 tracks.push({track:tr,name,noteOn,noteOff,lastNoteOffTick:lastNoteOff,lastEventTick:tick,endOfTrackTick});off=end;
}
tempos.sort((a,b)=>a.tick-b.tick);
function secondsAt(target){let cursor=0,seconds=0,us=500000;for(const event of tempos){if(event.tick>target)break;seconds+=(event.tick-cursor)*us/(division*1e6);cursor=event.tick;us=event.microsecondsPerQuarter;}return seconds+(target-cursor)*us/(division*1e6);}
const endTick=Math.max(...tracks.map(t=>t.lastEventTick)),lastNoteOffTick=Math.max(...tracks.map(t=>t.lastNoteOffTick));
const duration=secondsAt(endTick),noteDuration=secondsAt(lastNoteOffTick),quarterNotes=endTick/division;
const bpms=[...new Set(tempos.map(t=>60e6/t.microsecondsPerQuarter))];
const checks=[];function check(name,passed,detail){checks.push({name,passed,detail});if(!passed)fail(`${name}: ${detail}`);}
check('midi_tempo_128',bpms.length===1&&Math.abs(bpms[0]-128)<1e-9,`Parsed tempo: ${bpms.join(', ')} BPM`);
check('midi_256_quarters',quarterNotes===256,`End tick ${endTick}, PPQ ${division}, quarters ${quarterNotes}`);
check('midi_total_120_seconds',Math.abs(duration-120)<1e-9,`Tempo-integrated end: ${duration}s`);
check('midi_notes_end_within_120',noteDuration<=120+1e-9,`Last note-off: ${noteDuration}s`);
check('midi_note_pair_counts',tracks.reduce((n,t)=>n+t.noteOn,0)===tracks.reduce((n,t)=>n+t.noteOff,0),'Note-on/off event counts match; this is not a full musical/sonic audit');
check('plan_73_slots',plan.shots.length===73,`${plan.shots.length} slots`);
check('plan_256_beats',plan.shots.reduce((n,s)=>n+s.beat_length,0)===256,'256 planned beats');
let cursor=0,beat=0;
for(const shot of plan.shots){
 check(`${shot.id}_continuous`,shot.start_frame===cursor&&shot.beat_start_zero_based===beat,`Frame ${shot.start_frame}, beat ${shot.beat_start_zero_based}`);
 cursor=shot.end_frame_exclusive;beat=shot.beat_end_exclusive;
}
check('timeline_exact_120',cursor===2880&&plan.delivery.fps===24&&cursor/24===120,'2880 frames / 24fps = 120s');
const boundaries=plan.sections.map(s=>({section:s.id,beat_start:s.beat_start_zero_based??s.beat_start,beat_end:s.beat_end_exclusive,start_frame:s.start_frame,end_frame_exclusive:s.end_frame_exclusive,midi_start_tick:(s.beat_start_zero_based??s.beat_start)*division,midi_end_tick:s.beat_end_exclusive*division,midi_start_seconds:secondsAt((s.beat_start_zero_based??s.beat_start)*division),midi_end_seconds:secondsAt(s.beat_end_exclusive*division),timeline_start_seconds:s.start_frame/24,timeline_end_seconds:s.end_frame_exclusive/24}));
check('all_section_boundaries_match',boundaries.every(s=>Math.abs(s.midi_start_seconds-s.timeline_start_seconds)<1e-9&&Math.abs(s.midi_end_seconds-s.timeline_end_seconds)<1e-9),'All six MIDI tempo-integrated section boundaries equal 24fps plan boundaries');
check('music_design_matches',music.bpm===128&&music.beats===256&&music.durationSeconds===120,'Existing music-design agrees with MIDI and plan');
check('source_ids_no_legacy_paths',plan.source.sourceId==='FASTX10'&&plan.source.sourceFilename==='11 速度与激情10（2023）4K.mp4'&&!('file'in plan.source)&&plan.shots.every(s=>s.sourceId==='FASTX10'&&!('source_file'in s)),'Portable sourceId/sourceFilename only');
check('source_trims_still_unverified',plan.shots.every(s=>s.source_in_seconds===null&&s.source_out_seconds===null),'All 73 source trims remain null');
const absPathPattern=/[A-Za-z]:[\\/]/;
const inspectedNames=['plan.json','build-plan.mjs','shot-plan.csv','README_两分钟高燃剪辑方案.md','evidence/scout-index.json'];
check('no_hardcoded_drive_paths',inspectedNames.every(name=>!absPathPattern.test(fs.readFileSync(path.join(base,name),'utf8'))),'No hardcoded drive-letter paths in public plan/build/CSV/README/scout index');
check('scout_uses_filenames',scout.every(s=>typeof s.file==='string'&&!/[\\/]/.test(s.file)),'30 scout entries use plain image filenames');
const validation={schema:'fastx-120/validation-v1',status:'passed',checks,source_locator:{sourceId:plan.source.sourceId,sourceFilename:plan.source.sourceFilename,private_path_included:false},
 midi:{file:midiName,sha256:crypto.createHash('sha256').update(buf).digest('hex'),format,trackCount,division_ppq:division,tempo_events:tempos,bpm_values:bpms,time_signatures:timeSignatures,tracks,total_ticks:endTick,quarter_notes:quarterNotes,bars_at_4_4:quarterNotes/4,duration_seconds:duration,last_note_off_seconds:noteDuration},
 timeline:{slots:plan.shots.length,beats:beat,fps:24,total_frames:cursor,duration_seconds:cursor/24,section_boundaries:boundaries},
 audio_container_note:{reported_aac_container_duration_seconds:120.021333,attribution:'既有ffprobe验收结果；本脚本未重测；AAC编码padding',timeline_duration_seconds:120,changes_timeline_duration:false},
 limitations:['MIDI解析核对tempo、ticks、音符结束和章节边界，不等于试听/最终混音验收','未验证73槽源入出点或连续可用片段','未渲染电影或修改图片']};
fs.writeFileSync(path.join(base,'validation.json'),JSON.stringify(validation,null,2),'utf8');
console.log(JSON.stringify({status:validation.status,midiBpm:bpms,midiDuration:duration,lastNoteOff:noteDuration,slots:plan.shots.length,beats:beat,frames:cursor,sections:boundaries.map(s=>[s.midi_start_seconds,s.midi_end_seconds]),sourcePortable:true}));
