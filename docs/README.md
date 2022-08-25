# 谱面全局处理逻辑

## Arcaea 侧谱面处理逻辑

1. 解压传入的谱面文件，检查内部是否有存在的 aff 文件。

2. 对 aff 文件逐行进行以下分析：

   1. 设置第 1 行的 `AudioOffset` 值。
   2. 搜索全文可见 `Timing Group` 配置，并实例化对应 `Timing Group`。
   3. 搜索全文可见以 `timing` 开头的行，并自动分析，将其加入对应 `Timing Group` 的 `BPM List`。
   4. 逐行将 `(time, trace)` 形式的 `Tap` 实例化，并将其以字典形式追加到对应 `Timing Group` 的 `TapList` 里。计算其每一帧时所位于轨道的相对位置，并追加在对应实例的 `PositionList` 列表里。
   5. 逐行将 `arc(...)` 形式的 `Arc` 计算逐帧所在位置，并追加在对应实例的 `PositionList` 列表里；计算其每 `1/100` 帧间隔的 Arc 切片中心点与第 1 帧切片中心点的 `x, y, z` 坐标插值，并将其追加到 `deltaPosition` 列表里。并将实例本身以字典形式追加在对应 `Timing Group` 的 `ArcList` 列表里。
   6. 逐行将 `hold(...)` 形式的 `Hold` 计算逐帧所在的起始结束位置，并追加在对应的 `PositionList` 里。并将实例本身以字典形式追加在对应 `Timing Group` `HoldList` 列表里。
   7. 忽略所有 `HideGroup`，`Camera` 等的字样。这些内容将会在下个大版本中被加入。对于以上所有的 `Note`，将其产生一个 `Combo` 的时间戳追加到全局列表 `ComboNow` 中。

## Phigros 侧纯谱面视频转换逻辑

1. 创建以四个轨道和歌曲本身背景为背景的底图。将其应用于 60FPS 生成视频的每一帧。
2. 对于存在的每个 `Timing Group` 里所有的 `Note`，按照顺序进行逐帧绘制，并使用 `OpenCV` 进行透视变换。特殊地，对于 Arc：

> 将立体的 Arc 横向*切分*成 `100` 份，对应 `Y_Position` 的每 `0.01` 值。将 Arc 中心点落在任一*切分*上的 Arc 切片绘制在一个图层上。最后，对每一帧的每一个图层进行分别的透视变换，生成最后的单帧图片。

## Phigros 侧谱面视频元素处理逻辑

1. 对于 `ComboNow` 中的每个时间戳所对应的图片，将其 Combo 数增加 1，同时更新其分数。*注：为模拟 Phigros 环境，所有的 Hold 和 Arc 记为 1 Combo。*

2. 将音乐音频对应位置加入打击音。
3. 合成视频。
