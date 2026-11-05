# 咒术第一季 · 全集60Hz JPG素材库

24集共 **2,061,018个JPG采样路径**，对应 **823,577个独立源帧ID**。全部路径均已归档；重复采样使用tar硬链接保存，不丢弃重复路径。原始JPG为640×360/q6；60Hz是采样时间网格，源视频为23.976fps，重复采样不代表插帧生成新画面。

每集一个`S1E01.tar.gz`至`S1E24.tar.gz`，gzip level 1，每档小于2GiB。每档内包含同名集目录、该集全部`minute-NNN/Fxxxxxxx.jpg`、`index.sqlite`、`samples.jsonl`和实际生成的进度/校验元数据。独立源帧保留regular JPEG，重复样本保留指向同档先前JPEG的hardlink条目。

## 下载与恢复

下载全部24个归档、`restore_jpg.py`、`jpg-manifest.json`。Python 3.9或更新版本即可，仅用标准库，无须安装其他依赖或管理员权限。

在下载目录打开PowerShell，执行：

```powershell
python -X utf8 .\restore_jpg.py . --destination D:\JJK-JPG --manifest .\jpg-manifest.json
```

脚本会先验证每档字节数及SHA-256，再恢复全部路径；Windows/NTFS会优先创建硬链接。目标盘不支持硬链接或创建失败时，自动复制相同JPEG字节，最终路径仍完整。复制模式需要更多空间。恢复过程逐个核验全部原生JPEG的SHA-256与SQLite一致，核对每个样本连续编号、路径存在及字节数，完成后写`S1E01.restore-report.json`等报告。

也可仅恢复某一集：

```powershell
python -X utf8 .\restore_jpg.py .\S1E01.tar.gz --destination D:\JJK-JPG --manifest .\jpg-manifest.json
```

中断后加`--resume`重新运行同一命令。它重新校验归档并复核/恢复已有路径。明确需要全部复制而不用硬链接时，加`--copy`。脚本会拒绝越界路径、符号链接、重复归档条目，以及不指向同档先前原生JPEG的硬链接。

恢复后的目录示例：

```text
D:\JJK-JPG\S1E01\minute-000\F0000000.jpg
D:\JJK-JPG\S1E01\minute-000\F0000001.jpg
...
D:\JJK-JPG\S1E24\index.sqlite
```

## 清单与验收

`jpg-manifest.json`提供24档的精确字节数、SHA-256、JPG路径数、regular/hardlink数及源帧ID数。`SHA256SUMS-JPG.txt`可用于其他校验软件。

发布前已实际流式读遍每个归档：全部原生JPEG的SHA-256/字节数与该集只读SQLite核对；全部采样序号/路径连续；全部硬链接指向本档先前出现且源帧ID匹配的regular JPEG；元文件与源文件逐字节SHA一致。只有通过这些检查才生成可发布标记。恢复工具另已完整恢复S1E01全部86,102个JPG路径，核验34,406原生JPEG与51,696个真实NTFS硬链接；真实JPEG小样的强制复制回退也已通过。

## 重新打包（维护者）

`pack_jpg.py`以只读方式访问工作区源库，不修改源图或已封存内容：

```powershell
python -X utf8 .\pack_jpg.py --source "D:\源库\素材集_60Hz_JPG" --output . --episodes S1E01 --workers 1
python -X utf8 .\pack_jpg.py --source "D:\源库\素材集_60Hz_JPG" --output . --workers 3
```

每集`*.progress.json`为原子更新的实际进度；`*.verified.json`为归档实读校验报告。失败会记录`state: failed`及异常，并保留partial以供诊断；再次运行会安全重打未完成的集。已经完整写出的归档会直接重验，通过且SHA未变的归档会复用。打包读取SQLite时使用`mode=ro&immutable=1`，不创建源库协调文件；归档排除SQLite瞬态`-wal/-shm/-journal`文件。
