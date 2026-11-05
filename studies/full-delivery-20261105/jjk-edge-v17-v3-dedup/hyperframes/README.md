# 画面去重 V3 · HyperFrames

请先读[主说明](../README.md)。本次从V2复制工程后独立修改；源镜头重新选择，音乐master与67个切点不变。

改`edit.json`后运行`composition.py`，再执行`render.py --work 你自己的缓存目录`。所有复杂字效、动态alpha、撕边和空间布局保留独立源码。不要只携带HTML，旁边的assets与Python文件也必须保留。

空间窗口是实拍/动画素材的实时框选，不标为动态抠像。透明人物来自实际源RGB与人工轮廓/LK/GrabCut，发丝与裁切边存在近似，未用生成模型补全人体。声音仍为edge147–207秒；本版未重新试听。
