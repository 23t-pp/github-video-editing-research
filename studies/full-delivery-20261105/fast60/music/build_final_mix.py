"""Rebuild two unity-gain PCM24 stems and their bit-exact summed master.
Reads the locked edit.json and already-trimmed cues. No source video changes.
Dependencies: numpy, scipy, soundfile, FFmpeg. No cloud processing.
"""
from pathlib import Path
import os,json,hashlib,subprocess,io
import numpy as np
from scipy import signal
import soundfile as sf
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent/'hyperframes';OUT=PROJECT/'assets/audio'
SR=48000;N=2880000;PCM=8388608
FF=os.environ.get('FFMPEG_PATH',str(Path.home()/'Apps/ffmpeg/bin/ffmpeg.exe'))
edit_bytes=(PROJECT/'edit.json').read_bytes();edit=json.loads(edit_bytes.decode('utf-8-sig'))
assert edit['fps']==24 and edit['durationFrames']==1440
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rms(x):return float(np.sqrt(np.mean(x*x)))
def db(v):return float(20*np.log10(max(float(v),1e-12)))
def measure(p):
    r=subprocess.run([FF,'-nostdin','-hide_banner','-i',str(p),'-af','loudnorm=I=-16.5:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True)
    if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-3000:])
    text=r.stderr.decode(errors='replace');s=text.rfind('{');m,_=json.JSONDecoder().raw_decode(text[s:])
    return {'integrated_lufs':float(m['input_i']),'true_peak_dbtp':float(m['input_tp']),'lra_lu':float(m['input_lra']),'threshold_lufs':float(m['input_thresh'])}
score,sr=sf.read(OUT/'score.wav',dtype='float64',always_2d=True)
assert sr==SR and score.shape==(N,2)
source=np.zeros_like(score);envelope=np.zeros(N);records=[]
hp=signal.butter(2,95,'highpass',fs=SR,output='sos')
lp=signal.butter(2,10000,'lowpass',fs=SR,output='sos')
for shot in edit['shots']:
    if not shot.get('cue') or shot.get('sourceGain',0)<=0:continue
    cue=PROJECT/shot['cue'];cue_bytes=cue.read_bytes();x,sr=sf.read(io.BytesIO(cue_bytes),dtype='float64',always_2d=True)
    assert sr==SR and x.shape[1]==2
    start=round(shot['startFrame']*SR/edit['fps']);length=round(shot['frames']*SR/edit['fps'])
    if len(x)<length:raise ValueError(f"{shot['id']}: cue shorter than shot")
    x=x[:length].copy()
    x=signal.sosfilt(lp,signal.sosfilt(hp,x,axis=0),axis=0)
    fade_in=.006;fade_out=min(.065,length/SR*.10)
    if shot['id'] in ['S03','S04','S05','S10','S14','S35']:fade_in=.003;fade_out=min(.028,length/SR*.07)
    if shot['id']=='S42':fade_in=.25;fade_out=.38
    fi=max(1,round(fade_in*SR));fo=max(1,round(fade_out*SR))
    fade=np.ones(length);fade[:fi]=np.sin(np.linspace(0,np.pi/2,fi))**2;fade[-fo:]=np.sin(np.linspace(np.pi/2,0,fo))**2
    x*=fade[:,None]
    # Respect edit sourceGain. Only attenuate the unusually strong mixed cues:
    # their sustained RMS cannot exceed 45% of concurrent music RMS. No quiet
    # cue is normalized upward, which would also raise the original film BGM.
    requested=shot['sourceGain'];music_rms=rms(score[start:start+length]);cue_rms=rms(x*requested)
    cap=max(music_rms,.025)*.45
    correction=min(1,cap/max(cue_rms,1e-12))
    x*=requested*correction
    # Keep source texture with very mild transient following. Baseline .88,
    # max 1; this is not stem separation or an SFX classifier.
    energy=np.mean(x*x,axis=1)
    local=signal.lfilter([1-np.exp(-1/(SR*.012))],[1,-np.exp(-1/(SR*.012))],energy)
    normalized=np.sqrt(local)/(np.sqrt(np.max(local))+1e-12)
    articulation=.88+.12*normalized
    x*=articulation[:,None]
    source[start:start+length]+=x
    envelope[start:start+length]=np.maximum(envelope[start:start+length],normalized*min(rms(x)/.06,1))
    records.append({'id':shot['id'],'cue':shot['cue'],'cue_sha256':hashlib.sha256(cue_bytes).hexdigest(),'source_film':shot['film'],'source_in_sec':shot['sourceIn'],'start_frame':shot['startFrame'],'start_sample':start,'samples':length,'frames':shot['frames'],'start_sec':start/SR,'end_sec':(start+length)/SR,'edit_source_gain':requested,'additional_rms_cap_gain':correction,'fade_in_sec':fade_in,'fade_out_sec':fade_out,'music_rms_dbfs':db(music_rms),'processed_source_rms_dbfs':db(rms(x)),'processed_source_sample_peak_dbfs':db(np.max(np.abs(x)))})
# Slow, shallow music automation, max 0.65 dB under the active source cues.
# It leaves the score as the main continuous bed instead of pumping per cut.
smoothed=signal.lfilter([1-np.exp(-1/(SR*.05))],[1,-np.exp(-1/(SR*.05))],envelope)
music_duck_db=-.65*np.clip(smoothed,0,1)
score*=10**(music_duck_db[:,None]/20)
source[-9600:]*=np.linspace(1,0,9600)[:,None]
raw=score+source
temporary=ROOT/'mix-unmastered.wav';sf.write(temporary,raw,SR,subtype='FLOAT')
raw_measurement=measure(temporary)
target_lufs=-16.5;true_peak_ceiling=-1.6
common_gain_db=min(target_lufs-raw_measurement['integrated_lufs'],true_peak_ceiling-raw_measurement['true_peak_dbtp'])
common_gain=10**(common_gain_db/20)
qscore=np.rint(score*common_gain*PCM).astype(np.int32)
qsource=np.rint(source*common_gain*PCM).astype(np.int32)
qmaster=qscore+qsource
assert max(np.max(abs(qmaster)),np.max(abs(qscore)),np.max(abs(qsource)))<PCM
arrays={'score-mix.wav':qscore,'source-mix.wav':qsource,'master.wav':qmaster}
for name,q in arrays.items():sf.write(OUT/name,q<<8,SR,subtype='PCM_24')
temporary.unlink()
files={}
for name in arrays:
    file=OUT/name;info=sf.info(file)
    decoded=subprocess.run([FF,'-nostdin','-v','error','-xerror','-i',str(file),'-f','null','-'],capture_output=True)
    if decoded.returncode:raise RuntimeError(decoded.stderr.decode(errors='replace'))
    files[name]={'path':'assets/audio/'+name,'sha256':sha(file),'bytes':file.stat().st_size,'sample_frames':info.frames,'sample_rate':info.samplerate,'channels':info.channels,'subtype':info.subtype,'loudness':measure(file),'full_decode_exit_code':decoded.returncode}
a,_=sf.read(OUT/'score-mix.wav',dtype='int32',always_2d=True);b,_=sf.read(OUT/'source-mix.wav',dtype='int32',always_2d=True);m,_=sf.read(OUT/'master.wav',dtype='int32',always_2d=True)
error=(a.astype(np.int64)>>8)+(b.astype(np.int64)>>8)-(m.astype(np.int64)>>8)
assert (PROJECT/'edit.json').read_bytes()==edit_bytes,'edit.json changed during mixing; rerun after media lock'
assert all(sha(PROJECT/r['cue'])==r['cue_sha256'] for r in records),'cue changed during mixing; rerun after media lock'
automation={'edit_sha256':hashlib.sha256(edit_bytes).hexdigest(),'source_gain_basis':'Current locked edit.json shots[].sourceGain; never normalize quiet original mixed cues upward.','filters':{'highpass_hz':95,'lowpass_hz':10000,'type':'causal Butterworth, order 2 each'},'source_articulation':{'floor':.88,'ceiling':1,'energy_attack_ms':12},'maximum_music_duck_db':.65,'common_gain_db':common_gain_db,'cue_placements':records}
(ROOT/'mix-automation.json').write_text(json.dumps(automation,ensure_ascii=False,indent=2),encoding='utf-8')
np.savez_compressed(ROOT/'mix-envelopes.npz',sample_rate=SR,music_duck_db=music_duck_db.astype(np.float32))
report={'passed':bool(np.max(np.abs(error))==0 and all(v['sample_frames']==N and v['channels']==2 and v['sample_rate']==SR for v in files.values())),'duration_sec':60,'sample_frames':N,'cue_count':len(records),'edit_sha256':automation['edit_sha256'],'original_score_sha256':sha(OUT/'score.wav'),'s04':next(r for r in records if r['id']=='S04'),'mastering':{'method':'One shared linear gain applied to both stems; no independent nonlinear processing on the final master.','unmastered_measurement':raw_measurement,'target_integrated_lufs':target_lufs,'true_peak_ceiling_dbtp':true_peak_ceiling,'common_gain_db':common_gain_db},'files':files,'sum_validation':{'format':'decoded signed 24-bit integer samples','max_absolute_error_lsb':int(np.max(np.abs(error))),'different_samples':int(np.count_nonzero(error)),'equivalence':'score-mix + source-mix at unity equals master exactly in PCM24.','occ_volume_each':1},'listened':False,'limitations':['No authoring-agent listening has been performed. Waveform/loudness validation is not listening acceptance.','Source cues retain film music/dialogue/effects; filtering and low gains do not isolate pure engines/SFX.','Labels such as engine/helicopter are inherited from the shot plan, not verified by audio classification.']}
(ROOT/'final-mix-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
final=files['master.wav']['loudness'];s04=report['s04']
lines=['# 弯心 / APEX：双分轨与最终总声','',
       '三条文件均为60秒、48kHz、立体声、PCM24，精确2,880,000个采样帧。',
       '',
       '- `hyperframes/assets/audio/score-mix.wav`：已自动化和统一增益后的原创配乐。',
       '- `hyperframes/assets/audio/source-mix.wav`：按锁定镜头表铺设的30条原混音cue，含引擎、动作等声音，也可能保留影片原配乐、对白。',
       '- `hyperframes/assets/audio/master.wav`：上述两条的精确求和。',
       '',
       '**OpenChatCut中两条分轨各设音量1，才能重建master；不要再叠加master或原始score.wav，不要同时打开原视频音轨。** 如只需成品总声，单独使用master即可。',
       '',
       '## 本轮实际测量',
       '',
       f"总声综合响度 **{final['integrated_lufs']:.2f} LUFS**，真峰值 **{final['true_peak_dbtp']:.2f} dBTP**，LRA **{final['lra_lu']:.2f} LU**。三条均经过FFmpeg完整解码，文件采样数/采样率/通道数检查通过。", 
       '',
       f"PCM24整数域逐采样验证：`score-mix + source-mix - master`最大绝对误差 **{report['sum_validation']['max_absolute_error_lsb']} LSB**，非零差异样本 **{report['sum_validation']['different_samples']}**。总声仅使用两轨共同的线性增益，未在master上另加无法回分到两轨的非线性处理。", 
       '',
       '|文件|综合响度 LUFS|真峰值 dBTP|LRA LU|',
       '|---|---:|---:|---:|']
for name,entry in files.items():
    m=entry['loudness'];lines.append(f"|{name}|{m['integrated_lufs']:.2f}|{m['true_peak_dbtp']:.2f}|{m['lra_lu']:.2f}|")
lines += ['', '## 剪辑与包络', '',
          '按`shots[].startFrame`精确定位，每个24fps画面帧对应2000个音频采样；每条cue从自身第0个采样开始，截取`frames × 2000`个采样，不再重复加sourceIn。sourceIn仅记录源片取样证据。', '',
          f"S04采用片{s04['source_film']}、原片入点{s04['source_in_sec']}秒，锁定sourceGain={s04['edit_source_gain']}。输入edit.json SHA256：`{report['edit_sha256']}`；全部cue的SHA256、放置位置和包络参数在`mix-automation.json`。", '',
          '原声先做95Hz高通与10kHz低通，弱化原混音中无关低频/高频；通用淡入6ms、淡出最长65ms，短动作镜头3ms/最长28ms，S42采用250ms/380ms。它们用于抑制剪接爆音，不改变画面对齐。', '',
          'sourceGain严格采用镜头表作为基准；只有过强cue额外向下约束，让其持续RMS不超过同期配乐参考RMS的45%。安静cue不会被自动拉响，避免一并抬高影片原BGM。轻微能量跟随包络在0.88–1范围，音乐仅作最多0.65dB的浅让位。滤波、包络和RMS约束都不是人声/配乐分离，不能保证原声完全没有电影音乐。', '',
          f"最后两轨共同增益{common_gain_db:.3f}dB，目标−16.5 LUFS，并以−1.6dBTP限制共同增益上界。此方法保留情绪段落的动态，最终值以实测为准。分轨量化后用整数相加生成master，确保重新叠加时没有一轨被重复母带处理。", '',
          '## 重建命令', '',
          '使用已有numpy/scipy/soundfile的Python和FFmpeg，从工作区根运行：', '',
          '```powershell',
          "$mixPython = '.\\work\\reference-library-20261105\\audio-env\\Scripts\\python.exe'",
          "& $mixPython '.\\outputs\\fast60\\music\\build_final_mix.py'", '```', '',
          'FFmpeg不在默认工具目录时，先设置`FFMPEG_PATH`。若没有上例venv，可另建隔离Python环境，并安装本目录`requirements-score.txt`的三个依赖，再用该Python运行同一脚本；无需分离模型。脚本读取当前edit.json、score.wav和cue文件，输出两分轨、总声、报告和自动化参数；修改cue后必须重跑，旧报告的SHA不能代表新cue。执行末尾会核对edit.json及所有cue未在混音期间被修改。`mix-envelopes.npz`保留逐采样音乐让位曲线，主编辑参数在Python源码与mix-automation.json中。', '',
          '## 验收范围', '',
          '**制作代理没有实际监听。** 本轮完成的是信号/文件验收，未宣称听过引擎、擦撞或直升机声音；这些分类来自镜头表。人工仍需试听原配乐残留、源声是否刺耳、音乐是否被遮蔽、画面声响是否主观同步，以及耳机/小扬声器的低频表现。响度、峰值与精确求和通过，不能替代这些听感判断。', '']
(ROOT/'FINAL-MIX.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'cue_count':len(records),'master':files['master.wav']['loudness'],'common_gain_db':common_gain_db,'sum_error_lsb':report['sum_validation']['max_absolute_error_lsb']}))
assert report['passed']
