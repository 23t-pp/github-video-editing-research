from pathlib import Path
import json,numpy as np,soundfile as sf
R=Path(__file__).resolve().parent
r=json.loads((R/'analysis.json').read_text(encoding='utf-8'));c=r['tracks']['candidate'];m=r['tracks']['mixed']
top=sorted(sorted(c['onsets'],key=lambda e:e['flux_strength_p95_units'],reverse=True)[:24],key=lambda e:e['time_sec'])
x,sr=sf.read(R/c['audition_copy']['file'],always_2d=True);x/=10**(c['audition_copy']['linear_gain_db']/20)
bounds=[0,4.710385,10.162290,13.638435,19.035918,24.013946,28.826531,29.423764,30]
sections=[]
for a,b in zip(bounds[:-1],bounds[1:]):
    v=x[round(a*sr):round(b*sr)];sections.append({'start':a,'end':b,'rms_dbfs':round(float(20*np.log10(np.sqrt(np.mean(v*v))+1e-12)),2),'basis':'Convenient waveform/onset anchor segmentation, not a confirmed musical phrase boundary.'})
recommend={'selection':'audio/music-candidates/V07__music-candidate.m4a','duration_frames_25fps':750,'duration_sec':30,'last_frame_index_zero_based':749,'last_frame_interval_sec':[29.96,30],'native_audio_frames_to_trim':8,'time_stretch':False,'loop':False,'new_composition':False,'initial_mix_gain_suggestion_db':-6.4,'gain_basis':'Candidate level −9.6 LUFS to about −16 LUFS; subsequent car-SFX mix must be remeasured.','observed_audio_end_minus55_dbfs':c['active_above_minus55_dbfs']['last_sec'],'priority_onsets':top,'candidate_waveform_segments':sections,'beat_claim':'No confirmed beat/downbeat map. Approximately 100/50 BPM periodicity only.'}
(R/'editing-markers.json').write_text(json.dumps(recommend,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# V07原音乐复用：采样长度、波形结构和画面对齐','',
       '**当前范围：直接用音乐库内V07原音乐，按音乐时长剪片；不延长、不循环、不变速、不创作新曲。** 没有生成60秒版本，也没有使用旧Fast60的128 BPM配乐。制作代理没有实际监听；以下是解码与信号分析，不是已听辨的曲式/歌名/强拍确认。','',
       '## 长度与25fps末帧','',
       '|版本|原生解码采样帧 / 44.1kHz双声道|实际解码时长|25fps最近帧数|',
       '|---|---:|---:|---:|',
       f"|库内音乐主体候选|{c['decoded_sample_frames']:,}|{c['decoded_duration_sec']:.9f}s|750帧 / 30.000s|",
       f"|库内原混合轨|{m['decoded_sample_frames']:,}|{m['decoded_duration_sec']:.9f}s|751帧 / 30.040s|",'',
       '**建议新片用750帧，25fps，结束边界30.000秒。** 最后一张显示帧的零基编号749，从29.960显示至30.000秒。候选只多8个44.1k采样帧，即0.181406毫秒，处于极低电平尾部；输出时裁掉这8个尾部采样，不改变音乐速度。原参考视频30.04秒/751帧末尾那一帧，不是延长库内候选音乐的理由。M4A容器时长含AAC封装/预滚信息，不能代替解码长度。若项目用48kHz，可正常重采样后裁至1,440,000采样帧，不做tempo变化。','',
       f"有效活动以20ms立体声RMS>−55dBFS定义：候选开头约{c['active_above_minus55_dbfs']['first_sample']/44100:.6f}秒出现低电平活动，末点约{c['active_above_minus55_dbfs']['last_sec']:.6f}秒；其后约{c['active_above_minus55_dbfs']['trailing_sec']:.6f}秒低于门槛。−40dBFS门槛下末点为{c['active_above_minus40_dbfs_last_sec']:.6f}秒。这里不是宣称永久全零或听觉绝对静音，AAC微量尾噪仍延伸到文件末尾。不要裁掉这段参考原有收尾后又另造尾音。",'',
       '## 选择候选版的理由与不能证明的事','',
       '|信号指标|音乐主体候选|原混合轨|','|---|---:|---:|',
       f"|综合响度|{c['loudness']['integrated_lufs']:.2f} LUFS|{m['loudness']['integrated_lufs']:.2f} LUFS|",
       f"|FFmpeg实测真峰值|{c['loudness']['true_peak_dbtp']:.2f} dBTP|{m['loudness']['true_peak_dbtp']:.2f} dBTP|",
       f"|实际float解码采样峰|{c['sample_peak_dbfs']:.2f} dBFS|{m['sample_peak_dbfs']:.2f} dBFS|",
       f"|超出±1的解码通道采样数|{c['samples_above_full_scale_count']:,}|{m['samples_above_full_scale_count']:,}|",
       '|约0.6008s周期的谱通量自相关|0.3121|0.2190|', '',
       '候选版是此前真实UVR分离生成的Instrumental估计，作为库内配乐来源更方便与汽车动作原声分开控制。周期线索更清楚，且原混合轨有明显AAC解码超满幅，不能不减益就直接叠车声。**较清楚的周期、较低响度或分离模型的Instrumental命名都不能证明没有人声/SFX，也不能证明音色更好。** 本轮没有听辨音乐损伤、和声残留或听觉品质。','',
       '例如原混合轨14.700340秒有很强谱起音；候选相邻起音主要在14.753923秒，不能直接把原混合轨的起音表套给候选。分离前后局部事件改变不等于整体时间轴错位；大多数显著事件如10.162秒、28.209秒仍重合。','',
       '建议候选初始减益约6.4dB作为音乐bus，实测约−16 LUFS、−6.4dBTP；再加入低量汽车动作音效后重新测总声。这只是混音起点，不是已完成或已试听的总声。原混合轨保留作参考，不把其动漫对白/动作声当汽车音效一起铺入。','',
       '## 波形结构分区','',
       '以下分区以显著起音作为剪辑锚点，不冒称已确认的主歌、副歌、drop或小节边界。统计结构变化候选另见analysis.json：约0.792、3.262、5.108、6.937、9.108、13.386、15.488、18.416、21.200、25.405秒。它们来自频带能量前后0.6秒比较，时间解释粒度为数百毫秒，不能当sample级切点。','',
       '|范围|该段RMS dBFS|读法|','|---|---:|---|']
descriptions=['原音乐启动及早段高能簇；不另加独立音乐引子','能量相对低一些，适合保留运动连续性，末端接10.162强起音','10.162后有明显高能块，不能只按平均RMS持续快切','13.638起音后的段落含15.5附近能量簇','19.036起音后继续推进，保留局部疏密','24.014后是后段能量集中区，25.219/25.843/26.431/28.209可重点对齐','原有收尾与减弱；29.241仍有低电平起音，不应提前截断','低于−55dBFS门槛的原有尾部，画面可收束停留']
for s,desc in zip(sections,descriptions):lines.append(f"|{s['start']:.6f}–{s['end']:.6f}s|{s['rms_dbfs']:.2f}|{desc}|")
lines += ['', '## 优先画面对齐的真实起音候选','',
          '下表取候选音轨谱通量较强的24个事件并按时间排序。time_sec是原生44.1k波形短窗RMS上升锚点；低频渐起、混合音效、滤波和分析窗可能带来约10–20ms定位不确定性，不能把小数位当作听觉精度保证。25fps帧位为最近画面边界，最大量化偏差20ms。**这些是onset候选，不是确认的beat/downbeat。** 不建议156个检测事件全部切镜；按动作因果和运动连续性挑选。','',
          '|音频秒|44.1k采样编号|25fps零基帧|画面边界秒|量化误差ms|谱通量相对强度|','|---:|---:|---:|---:|---:|---:|']
for e in top:lines.append(f"|{e['time_sec']:.6f}|{e['sample_44100']}|{e['output_frame_25fps']}|{e['frame_time_sec']:.2f}|{e['frame_error_ms']:+.3f}|{e['flux_strength_p95_units']:.3f}|")
lines += ['', '## 节拍与工具的限制','',
          '原混合轨此前HF周期跟踪置信度0.132并拒绝稳定beat；分离候选为99.9 BPM、置信度0.18，仍很弱。本轮独立谱通量自相关最高约0.600816秒（99.864 BPM），另有1.198730秒（50.053 BPM）倍半速歧义。因此不沿用旧作128 BPM，不补一套整片100 BPM格线，更不把“音量大”直接叫强拍。已给出的原生起音时间比硬锁某个BPM更适合本次复刻。','',
          'analyze_v07.py实际用FFmpeg解码float32、numpy/scipy计算1024样本STFT（128样本hop，约2.902ms）、20ms RMS活动门槛、频带新颖度与短窗波形上升；全部本地运行，没有CUA、云上传、识曲或新分离。原生采样解码保留了原混音超满幅值，测量前没有先削波。','',
          '## 产物与复跑','',
          '- analysis.json：两个版本的完整指标、156/139个onset候选、100ms RMS和统计结构。',
          '- editing-markers.json：建议750帧、最后帧范围、优先事件、波形分区，方便主流程读取。',
          '- candidate-onsets.csv：候选全部起音、原生采样、25fps帧位与误差。',
          '- signal-overview.svg：100ms RMS与较强起音的对比图，竖线不是确认的beat。',
          '- V07-candidate-audition-minus16.wav / V07-mixed-audition-minus16.wav：仅线性减益后的比较试听副本，约−16.00 / −16.01 LUFS；保留原速原长度。未声称听过。',
          '- 没有延长版、循环版、新作曲或新生产声床。','',
          '从工作区根运行：','',
          '```powershell',
          "$v07Python = '.\\work\\reference-library-20261105\\audio-env\\Scripts\\python.exe'",
          "& $v07Python '.\\work\\reference-replay-v07\\audio\\analyze_v07.py'",
          "& $v07Python '.\\work\\reference-replay-v07\\audio\\write_report.py'",'```','',
          '依赖为numpy/scipy/soundfile和本地FFmpeg；FFmpeg可用FFMPEG_PATH覆盖。来源文件SHA256见analysis.json。库内输入文件及Fast60旧工程均未修改。','']
(R/'report.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'report':'report.md','markers':'editing-markers.json','duration_frames':750,'priority_onsets':len(top),'listened':False}))
