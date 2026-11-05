# HF整合与官方portable工程导出实录

实际项目：`0fd76ceb-875e-4507-be68-f296dd3dacfd`。确认源码的项目路由为`/#/editor/<projectId>`（[cli/session.ts:37](C:/Users/PC/Desktop/OpenChatCut-main/cli/session.ts:37)）。本机地址：`http://127.0.0.1:5199/#/editor/0fd76ceb-875e-4507-be68-f296dd3dacfd`。

HF成片实际导入走CLI `tools call import_assets --apply`，内部官方`executeOfflinePathImport → importLocalPaths → importAgentPaths`，不是手写媒体池记录。第二时间线通过`manage_timelines create`，片段通过`edit_item adds/updates`。

最终有两条时间线，均1920×1080、24fps、108帧：

- 原生：`tl_44436b4d-d623-4d92-9856-55be7bb7f7c7`，9个item，保留六格独立裁切/关键帧、静音视频与一条volume1 master。与加HF前的原生timeline深比较完全一致。
- HF整合：`tl_a0ae5ccd-1299-4d26-9289-285df57432f3`，1个video item（`item_91cd53cc-ed92-4395-9018-dc5d6402b143`），全局0–108、源0、volume1；内含HF成片的master音轨一次，不另叠master。主动将108帧作为剪辑长度，不按4.521333秒容器padding拉长。

8条新增HF阶段CLI均退出0、stderr为空。最终CLI与5199 HTTP完整ProjectDoc深比较相等。未开UI、未占用新项目、未执行导入副本验证；该步骤由主流程随后完成。

## 导出实现

不是只保存Doc，也没有重新实现@2编码器。实际程序化导入并调用官方：

- [src/persist/projectTransfer.ts:238](C:/Users/PC/Desktop/OpenChatCut-main/src/persist/projectTransfer.ts:238) `buildProjectExport(projectId,name)`。
- [src/persist/sharedKv.ts:43](C:/Users/PC/Desktop/OpenChatCut-main/src/persist/sharedKv.ts:43) `configureSharedKvBackend()`，使用已有backend seam注入**只读、仅新项目键**的本地HTTP GET适配。set/delete/keys/writeAgentRuntime/updateAgentRunLease均直接抛错，不能写运行库。
- 相对fetch仅在该独立Node进程内映射到`http://127.0.0.1:5199`；只允许GET项目entry和media/uploads，不改应用、配置或源码。
- 官方buildProjectExport清理originalFilePath，载入关联runtime，汇总媒体，调用[projectTransferStream.ts:108](C:/Users/PC/Desktop/OpenChatCut-main/src/persist/projectTransferStream.ts:108) `projectExportChunks()`生成manifest/media-start/media-chunk/media-end并返回Blob。保存的是此Blob的原始字节。

实际命令（工作目录桌面OpenChatCut-main）：

```powershell
& 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' --import tsx 'D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2/work/v05-sample/occ-export.mjs' --preflight
& 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' --import tsx 'D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2/work/v05-sample/occ-export.mjs' --final
```

preflight在HF未加入时先实际调用官方函数，得到含3份媒体、8,313,952字节的内存包；未写交付包。第一轮尝试把Windows绝对路径直接给`--import`，Node报ERR_UNSUPPORTED_ESM_URL_SCHEME；改用repo工作目录的`--import tsx`即成功。这是导出脚本启动参数修正，没有改产品代码。

final在HF时间线与资产存在后才运行，生成：

`outputs/v05-six-panel/openchatcut/V05六格卡片_可编辑工程.ccproj`

格式：`openchatcut-project@2`；大小：**14,488,547字节**；SHA256：`226547ebaa9be651936928a434bdd6b98c1a789ba74da129ff4043deef285583`。

mediaTotal=4，mediaMissing=[]。包含A短片2,273,955字节、B短片3,496,332字节、master WAV432,044字节、HF成片4,618,705字节。逐项base64解码、校验media-start声明大小、与本机服务对应src原始媒体逐字节比较，全部一致。还检查了Doc媒体引用全覆盖、无重复src、无未结束媒体记录、单行/单媒体未超官方上限、Doc无originalFilePath。

最终Doc已更新`outputs/v05-six-panel/openchatcut/完整工程Doc.json`、`原生工程Doc.json`及读取快照；其中Doc是结构审计，`.ccproj`才是带媒体可移植工程。

## 下一步UI导入验证

官方入口为Dashboard“导入工程”（[DashboardViews.tsx:87](C:/Users/PC/Desktop/OpenChatCut-main/src/components/dashboard/DashboardViews.tsx:87)）；调用[projectTransfer.ts:482](C:/Users/PC/Desktop/OpenChatCut-main/src/persist/projectTransfer.ts:482) `importProjectPackage(file)`。它识别首行@2、分阶段恢复媒体、校验Doc并创建新项目，不应覆盖当前源项目。

请导入该.ccproj，记录返回的新项目UUID，检查两条时间线、六格关键帧与音轨、HF时间线0–108帧；画面与声音播放结果另作实际记录。当前包内字节验证已通过，但尚未把它冒称为UI导入/播放通过。

审计文件：`occ-export.mjs`、`occ-export-preflight.json`、`occ-portable-verification.json`、`occ-hf-integrate.mjs`、`occ-hf-verification.json`及hf-*命令/回执。

## 后续实际UI导入已完成

主流程已通过官方UI导入成功、显示素材4/4，创建副本`28fd7d1f-4659-4247-82eb-1a2e06f6f93d`。本子代理只读核验该副本：2时间线、4资产、9+1 item，所有clip时序/裁切/变换/关键帧/音量与导出前一致；4份媒体HTTP200，SHA256和字节数均与工程包携带数据一致。实际查看导入成功和六格独立轨截图，看到两序列、24fps、4.50秒及独立轨道。未控制UI、未修改正在编辑的副本、未试听。

最终证据：`outputs/v05-six-panel/evidence/OpenChatCut导入验证.json`，汇总本次UI导入与先前原生、音轨、HF整合和portable验证。上文“下一步/尚未”描述的是导出完成时的阶段状态，现已由此记录更新。
