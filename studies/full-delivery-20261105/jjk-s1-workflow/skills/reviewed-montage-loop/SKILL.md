---
name: reviewed-montage-loop
description: 在本项目用素材索引、设计审核、取片与执行代理、独立成片审核和编排监控完成至少四轮有实产物的混剪。用于继续或复用本工作流。
---

# 有证据的多代理混剪循环

先读项目`docs/设计规格.md`、`data/run-config.json`、`workflow/monitor.json`；本技能位于项目`skills`，上两级为工程根。运行参数由当前用户指令和冻结配置决定，不把本片V20或60秒当成所有未来影片默认。

编排层分派设计、源素材与独立审核；文件责任边界应互斥。设计可先写，审核通过对应阶段后才取高分素材和渲染。审核员不能是同轮执行者，证据必须绑定文件SHA，变更后需复审受影响范围。使用真实源PTS；60Hz采样重复明确标记，输出JPG与源片取回分开，未知语义保留unknown。

长任务由`scripts/monitor.py`每5秒记录磁盘、逐集计数和心跳；180秒无进度或任务失败触发编排层调查，再决定最多两次重试，不将失败改为通过。以`scripts/workflow.py status`查看状态，以`check-review --review <相对路径>`检查审核绑定。每个阶段后运行`workflow.py next`生成待派角色和动作，由编排层实际调用对应代理；CLI本身不假装已调起模型。审核放行范围分素材A、剪辑B、逐轮及最终，不互相冒充。

至少四轮，各有实际不同视频、计划、执行日志、独立审核、修订diff。推荐先做动作粗剪，再做复杂合成，之后全片高质量，最后按审核发现修订。每个loop目录保留`plan.json/execution.json/review.json/revision-diff.json`，`execution`包含executor与实际video相对路径，`review`包含reviewer/status与boundArtifacts。轮数够而P0/P1未解决就继续下一轮，不能自动验收。

取素材回原视频，不能把检索缩略JPG或低清review.mp4当成高分素材。复杂动态alpha只用当前季源像素；通用分屏或静态人像不能充当复杂转场复刻完成。复用字形/边缘算法可以，必须审实际渲染。

交付前检查素材集全部唯一JPEG解码和SHA、全部采样路径/别名/PTS；成片帧/采样数/连续性；HF真实CLI渲染；OCC官方导出与真实重导入；工程编辑边界和中文教程。全部实际通过后由独立审核写`reviews/最终验收.json`，运行`workflow.py seal`，它会拒绝少于四个不同视频或素材未完成的封存。不要在本技能中额外要求用户批准已经授权的本地可逆制作。
