"""这个模块用来初始化生成谱面的元素。

该模块负责生成的元素/实例：Tap, Hold, Sky Note, Arc, Timing Group.
"""


from bisect import bisect_left


class ArcChartException(Exception):
    """这个类用来抛出解析 Arcaea 谱面时的异常。
    """

    def __init__(self, exception_info):
        """该函数用来抛出 Arcaea 谱面解析异常。

        Args:
            exception_info (str): 异常发生时的说明。
        """
        super().__init__(self)
        self.exception_info = f"{exception_info}\n在向他人反馈问题时，请附带主目录下的 Log，报错内容和谱面文件以精确定位问题。"

    def __str__(self):
        return self.exception_info


def validate_trace(touch_time: float, note_type: str, trace: int):
    """该函数用来校验 Note 所在的轨道是否越界。

    对于所有的 Tap 和 Hold，它们所在的轨道编号只能是 1-4 中的一个整数。

    Args:
        touch_time (float): 该 Note 被打击或最初被打击的时间。
        note_type (str): 该 Note 的类型。
        trace (int): 该 Note 所在的轨道。

    Raises:
        ArcChartException: 抛出该异常，以说明这个 Note 所在的轨道不被允许。
    """
    if not 0 < trace < 5:
        raise ArcChartException(
            f"在处理打击时间为 {touch_time}s 的 {note_type} 时出现问题：轨道 {trace} 超出允许范围。")


def validate_position(touch_time: float, note_type: str, x_position: float, y_position: float):
    """该函数用来校验 Note 是否为超界的。

    Args:
        touch_time (float): 该 Note 被打击或最初被打击的时间。
        note_type (str): 该 Note 的类型。
        x_position (float): 该 Note 被打击，刚开始被打击或结束被打击的横向位置。
        y_position (float): 该 Note 被打击，刚开始被打击或结束被打击的纵向位置。
    """
    if x_position < 0 or x_position > 1:
        print(
            f"谱面时间为 {touch_time} 时，处于打击的 {note_type} 是非正常的超界 Note。其横向坐标为 {x_position}。")
    if y_position < 0 or y_position > 1:
        print(
            f"谱面时间为 {touch_time} 时，处于打击的 {note_type} 是非正常的超界 Note。其纵向坐标为 {y_position}。")


class NoteBase:
    """所有 Note 的基类。
    """

    def __init__(self, touch_time: float, note_type: int, bpm_list: dict) -> None:
        """该函数用来初始化生成所有 Note。

        Args:
            touch_time (float): 该 Note 被打击或最初被打击的时间。
            note_type (int): 该 Note 的按键类型：地键/Tap 为 1，长条/Hold 为 2，天键/Sky Note 为 3
                音弧/Arc 为 4，将会被最终转为黄键/Drag (5).
            bpm_list (dict): 该谱面的 BPM 列表。各子类初始化函数将会根据该字典来计算相对位置。
        """
        self.time_0_position = None
        self.bpm_list = bpm_list
        self.touch_time = touch_time
        self.note_type = note_type
        self.pos_per_frame = {}
        with open("../../song_total_time.txt", 'r', encoding="utf-8") as time_:
            self.song_total_time = time_.read()
        self.get_note_front_position(self.bpm_list)

    def get_note_front_position(self, bpm_list: dict):
        """该函数用来计算 Note 的前端位置。
        
        Args:
            bpm_list (dict): 该谱面的 BPM 列表。各子类初始化函数将会根据该字典来计算相对位置。
        """
        # 以下内容的实现逻辑：
        # 1. 通过 bpm_list 中，每一组 BPM 的持续时间和 BPM 值来逆推出每一个 Note 的起始位置。
        # 2. 通过 Note 的起始位置，来计算出每一帧，Note 的所在位置。
        # 该实现逻辑较为丑陋，需要后期优化。

        # 我们为该函数传入 bpm_list，并让它使用自身的 touch_time 去计算它的初始位置。
        # 此函数首先判断自己被打击时位于哪个 BPM 组，随后使用该 BPM 组及其前面的 BPM 组的持续时间和 BPM 值来计算自己的初始位置。
        # 随后该函数将会计算每 0.001s 时，Note 的相对位置。将其保存在自身的 pos_per_frame 字典中。

        # 初始化一个 Note 的起始位置。
        initial_position = 0
        # 计算需要计算的次数，即计算自己被打击时位于的 BPM 组是第几个。
        calculation_times = bisect_left(list(bpm_list.keys()), self.touch_time)
        # 将 bpm_list 中的所有 BPM 组的持续时间和 BPM 值，分别存入两个列表中。
        value_list, key_list = list(bpm_list.values()), list(bpm_list.keys())
        # 使用每一个 BPM 组的值，计算出该 Note 的初始位置。
        for which_bpm_item in range(0, calculation_times - 1, 1):
            initial_position += value_list[which_bpm_item] * \
                (key_list[which_bpm_item+1] - key_list[which_bpm_item])
        initial_position += value_list[calculation_times - 1] * \
            (self.touch_time - key_list[calculation_times - 1])
        # 将该 Note 的初始位置，保存在自身的 time_0_position 中。
        self.time_0_position = 0.001 * 0.001 * initial_position

        # this_frame_position 表示该 Note 在当前帧的位置。
        # 以下的计算从第 0 帧开始，故当前帧的位置就是该 Note 的初始位置。
        this_frame_position = self.time_0_position
        # 开始计算每一帧的位置。
        for play_time in range(0, self.touch_time + 1):
            if play_time == self.touch_time:
                self.pos_per_frame[play_time] = 0
            if play_time < self.touch_time:
                self.pos_per_frame[play_time] = this_frame_position
            if play_time > self.touch_time:
                pass
            # 将这一帧的位置保留给下一次计算。
            this_frame_position -= 0.001 * 0.001 * \
                value_list[bisect_left(list(bpm_list.keys()), play_time) - 1]


class Tap(NoteBase):
    """Tap Note 类
    """

    def __init__(self, touch_time: float, trace: int, bpm_list: dict[float, float]) -> None:
        """该函数用来生成一个 Tap Note。

        Args:
            touch_time (float): 该 Tap 被打击的时间。
            trace (int): 该 Tap 落在轨道的编号，以 1-4 中的一个整数表示。
        """
        validate_trace(touch_time, "Tap", trace)
        super().__init__(touch_time, 1, bpm_list)
        self.trace = trace


class Hold(NoteBase):
    """Hold Note 类
    """

    def __init__(self, start_time: float, end_time: float, trace: int, bpm_list: dict) -> None:
        """该函数用来生成一个 Hold Note。

        Args:
            start_time (float): 该 Hold 被开始打击的时间。
            end_time (float): 该 Hold 被结束打击的时间。
            trace (int): 该 Hold 落在轨道的编号。以 1-4 中的一个整数表示。
        """
        validate_trace(start_time, "Hold", trace)
        super().__init__(start_time, 2, bpm_list)
        self.end_time, self.trace = end_time, trace


class SkyNote(NoteBase):
    """Sky Note 类
    """

    def __init__(self, touch_time: float, x_position: float, y_position: float, bpm_list: dict) -> None:
        """该函数用来生成一个 Sky Note。

        Args:
            touch_time (float): 该 Sky Note 被打击的时间。
            x_position (float): 该 Sky Note 被打击时落在的位置。
            y_position (float): 该 Sky Note 被打击时落在的位置。
            bpm_list (dict): 该谱面的 BPM 列表。各子类初始化函数将会根据该字典来计算相对位置。
        """
        validate_position(touch_time, "Sky Note", x_position, y_position)
        super().__init__(touch_time, 3, bpm_list)
        self.x_position, self.y_position = x_position, y_position


class Arc(NoteBase):
    """Arc Note 类
    """

    def __init__(
        self, start_time: float, end_time: float, x_start_pos: float, y_start_pos: float, movement_type: str,
        x_end_pos: float, y_end_pos: float, arc_color: int, none_value: str, is_trace: bool, bpm_list: dict
    ) -> None:
        """该函数用来生成一个 Arc Note。

        Args:
            start_time (float): 该 Arc 被开始打击的时间。
            end_time (float): 该 Arc 被结束打击的时间。
            x_start_pos (float): 该 Arc 被开始打击时的横向位置（0-1 之间的浮点数）
            y_start_pos (float): 该 Arc 被结束打击时的纵向位置（0-1 之间的浮点数）
            movement_type (str): 该 Arc 的坐标变化移动类型。
            x_end_pos (float): 该 Arc 被结束打击时的横向位置（0-1 之间的浮点数）
            y_end_pos (float): 该 Arc 被结束打击时的纵向位置（0-1 之间的浮点数）
            arc_color (int): 该 Arc 的颜色（0 为蓝色，1 为红色，2 为绿色）
            none_value (str): 该 Arc 的 NONE 值。
            is_trace (bool): 该 Arc 是否为黑线。
            bpm_list (dict): 该谱面的 BPM 列表。各子类初始化函数将会根据该字典来计算相对位置。
        """
        # 验证轨道编号是否合法。
        validate_position(start_time, "Arc", x_start_pos, y_start_pos)
        validate_position(end_time, "Arc", x_end_pos, y_end_pos)
        self.end_time, self.x_start_pos, self.y_start_pos, self.movement_type, self.x_end_pos, self.y_end_pos, \
            self.arc_color, self.none_value, self.is_trace = end_time, x_start_pos, y_start_pos, movement_type, \
            x_end_pos, y_end_pos, arc_color, none_value, is_trace
        super().__init__(start_time, 4, bpm_list)
        self.duration = end_time - start_time
        if self.duration < 0:
            # 如果结束时间小于开始时间，抛出异常。
            raise ArcChartException(f"谱面时间为 0 时，处于打击的 Arc 具有不受支持的负持续时间。")

    def get_self_relative_position(self):
        if len(str(self.movement_type)) == 4: # 四种运动类型分别是 sisi，siso，sosi 和 soso
            pass
