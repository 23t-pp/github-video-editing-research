# 参考音轨与音乐主体候选库

> **直接学习：** 独立学习库ZIP解压后，按[库根README](../README.md)启动学习页，即可阅读并听已生成的音轨，无须重新运行分离模型。
>
> **完整重跑：** 需要自己的20条原视频，并还原 `outputs/reference-library-20261105/` 与 `work/reference-library-20261105/` 的工作区结构。先用库根 `scripts/prepare-manifest.mjs` 生成 `manifest.local.json`，再复制到 `work/reference-library-20261105/manifest.local.json`。分析依赖HyperFrames **0.8.216** 的精确 `dist/chunk-NOH32H42.js` 和montage **0.4.1** 本地模块；ZIP启动命令不会安装全部分析/模型依赖。最小目录树和PowerShell创建、复制命令见[完整重跑说明](../data/audio/processing-notes.md#怎样复跑)。

原始混合音轨20条；真实本地模型分离候选20条。所有曲名未识别，尚未实际听辨。候选可能残留对白、人声或SFX，也可能损伤音乐，不能当纯BGM保证。

BPM为信号分析候选；素材适用标签是剪辑建议，不是歌曲/乐器识别。原始混合轨适合研究原片音画关系；音乐主体候选需试听后再决定是否用来重新配画面。

|ID|原混合轨时长|BPM候选|周期信度|原混合轨|音乐主体候选|
|---|---:|---|---|---|---|
|V01|32.44s|139.9 / 69.9|较高周期线索；未听辨确认|[M4A](mixed/V01__mixed.m4a)|[M4A](music-candidates/V01__music-candidate.m4a)|
|V02|24.73s|128 / 64|较高周期线索；未听辨确认|[M4A](mixed/V02__mixed.m4a)|[M4A](music-candidates/V02__music-candidate.m4a)|
|V03|30.02s|88.5 / 177|中等周期线索；未听辨确认|[M4A](mixed/V03__mixed.m4a)|[M4A](music-candidates/V03__music-candidate.m4a)|
|V04|21.53s|123.9 / 61.9|较高周期线索；未听辨确认|[M4A](mixed/V04__mixed.m4a)|[M4A](music-candidates/V04__music-candidate.m4a)|
|V05|23.11s|140 / 93.4 / 56 / 96.9|低/存在冲突|[M4A](mixed/V05__mixed.m4a)|[M4A](music-candidates/V05__music-candidate.m4a)|
|V06|130.06s|105.9 / 53 / 212|低/存在冲突|[M4A](mixed/V06__mixed.m4a)|[M4A](music-candidates/V06__music-candidate.m4a)|
|V07|30.02s|100.2 / 50|低/无稳定拍点|[M4A](mixed/V07__mixed.m4a)|[M4A](music-candidates/V07__music-candidate.m4a)|
|V08|32.72s|140 / 70|较高周期线索；未听辨确认|[M4A](mixed/V08__mixed.m4a)|[M4A](music-candidates/V08__music-candidate.m4a)|
|V09|10.71s|109.3 / 54.9|低/无稳定拍点|[M4A](mixed/V09__mixed.m4a)|[M4A](music-candidates/V09__music-candidate.m4a)|
|V10|18.09s|80.1 / 160.2 / 40|较高周期线索；未听辨确认|[M4A](mixed/V10__mixed.m4a)|[M4A](music-candidates/V10__music-candidate.m4a)|
|V11|37.41s|140.1 / 70.1|中等周期线索；未听辨确认|[M4A](mixed/V11__mixed.m4a)|[M4A](music-candidates/V11__music-candidate.m4a)|
|V12|9.64s|135.2 / 102.2 / 51|低/存在冲突|[M4A](mixed/V12__mixed.m4a)|[M4A](music-candidates/V12__music-candidate.m4a)|
|V13|12.84s|112.9 / 56.5|中等周期线索；未听辨确认|[M4A](mixed/V13__mixed.m4a)|[M4A](music-candidates/V13__music-candidate.m4a)|
|V14|25.98s|149.9 / 75 / 99.8|中等周期线索；未听辨确认|[M4A](mixed/V14__mixed.m4a)|[M4A](music-candidates/V14__music-candidate.m4a)|
|V15|26.63s|122 / 81.2|低/存在冲突|[M4A](mixed/V15__mixed.m4a)|[M4A](music-candidates/V15__music-candidate.m4a)|
|V16|24.45s|58.1|低/存在冲突|[M4A](mixed/V16__mixed.m4a)|[M4A](music-candidates/V16__music-candidate.m4a)|
|V17|25.85s|80.3 / 160.6|低/存在冲突|[M4A](mixed/V17__mixed.m4a)|[M4A](music-candidates/V17__music-candidate.m4a)|
|V18|59.00s|82.1 / 164.2|较高周期线索；未听辨确认|[M4A](mixed/V18__mixed.m4a)|[M4A](music-candidates/V18__music-candidate.m4a)|
|V19|19.44s|137.3 / 141.3|低/存在冲突|[M4A](mixed/V19__mixed.m4a)|[M4A](music-candidates/V19__music-candidate.m4a)|
|V20|30.67s|139.8 / 69.9|低/存在冲突|[M4A](mixed/V20__mixed.m4a)|[M4A](music-candidates/V20__music-candidate.m4a)|

完整元数据、SHA256、响度与分离说明见 [music-index.json](../data/audio/music-index.json)，方法见 [processing-notes.md](../data/audio/processing-notes.md)。

精确去重按文件、AAC编码内容和原生双声道PCM分别记录。无精确重复不代表不同BGM；未使用声纹相似当同曲确证。
