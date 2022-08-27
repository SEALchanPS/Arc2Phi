"""这个模块用来初始化生成谱面的元素。

该模块负责生成的元素/实例：Tap, Hold, Sky Note, Arc, Timing Group.
"""


class ArcChartException(Exception):
    """这个类用来抛出解析 Arcaea 谱面时的异常。
    """

    def __init__(self, error_info):
        """该函数用来抛出 Arcaea 谱面解析异常。

        Args:
            error_info (str): 异常发生时的说明
        """
        super().__init__(self)
        self.error_info = f"{error_info}\n在向他人反馈问题时，请附带主目录下的 Log，报错内容和谱面文件以精确定位问题。"

    def __str__(self):
        return self.error_info


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


class BaseNotes:
    """所有 Note 的基类。
    """

    def __init__(self, touch_time: float, note_type: int, bpm_list: dict) -> None:
        """该函数用来初始化生成所有 Note。

        Args:
            touch_time (float): 该 Note 被打击或最初被打击的时间。
            note_type (int): 该 Note 的按键类型：地键/Tap 为 1，长条/Hold 为 2，天键/Sky Note 为 3
                音弧/Arc 为 4，将会被最终转为黄键/Drag (5).
            bpm_list (dict): 该谱面的 bpmList。各子类初始化函数将会根据该字典来计算相对位置。
        """
        self.bpm_list = bpm_list
        self.touch_time = touch_time
        self.note_type = note_type
        self.pos_per_frame = {}
        with open("song_total_time.txt", 'r', encoding="utf-8") as time_:
            self.song_total_time = time_.read()
        self.get_starting_position(self.bpm_list)

    def get_starting_position(self, bpm_list: dict):
        pass


class Tap(BaseNotes):
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


class Hold(BaseNotes):
    """Hold Note 类
    """

    def __init__(self, start_time: float, end_time: float, trace: int, bpm_list: dict) -> None:
        """该函数用来生成一个 Hold Note。

        Args:
            start_time (float): 该 Hold 被开始打击的时间
            end_time (float): 该 Hold 被结束打击的时间
            trace (int): 该 Hold 落在轨道的编号。以 1-4 中的一个整数表示。
        """
        validate_trace(start_time, "Hold", trace)
        super().__init__(start_time, 2, bpm_list)
        self.end_time, self.trace = end_time, trace


class SkyNote(BaseNotes):
    """Sky Note 类
    """

    def __init__(self, touch_time: float, x_position: float, y_position: float, bpm_list: dict) -> None:
        """该函数用来生成一个 Sky Note。

        Args:
            touch_time (float): 该 Sky Note 被打击的时间
            x_position (float): 该 Sky Note 被打击时落在的位置
            y_position (float): 该 Sky Note 被打击时落在的位置
        """
        validate_position(touch_time, "Sky Note", x_position, y_position)
        super().__init__(touch_time, 3, bpm_list)
        self.x_position, self.y_position = x_position, y_position


class Arc(BaseNotes):
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
        """
        validate_position(start_time, "Arc", x_start_pos, y_start_pos)
        validate_position(end_time, "Arc", x_end_pos, y_end_pos)
        self.end_time, self.x_start_pos, self.y_start_pos, self.x_end_pos, self.y_end_pos, \
            self.arc_color, self.none_value, self.is_trace = end_time, x_start_pos, y_start_pos, \
            x_end_pos, y_end_pos, arc_color, none_value, is_trace
        super().__init__(start_time, 4, bpm_list)
