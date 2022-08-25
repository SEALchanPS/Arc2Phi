"""这个模块用来初始化生成谱面元素。
"""

import logging


class BaseNotes:
    """所有 Note 的基类。
    """

    def __init__(self, touch_time: float, note_type: int) -> None:
        """该函数用来初始化生成所有 Note。

        Args:
            touch_time (float): 该 Note 被打击或最初被打击的时间。
            note_type (int): 该 Note 的按键类型：地键/Tap 为 1，长条/Hold 为 2，天键/Sky Note 为 3
                音弧/Arc 为 4，将会被最终转为黄键/Drag (5).
        """
        self.touch_time = touch_time
        self.note_type = note_type


class Tap(BaseNotes):
    """Tap Note 类
    """

    def __init__(self, touch_time: float, trace: int) -> None:
        """该函数用来生成一个 Tap Note。

        Args:
            touch_time (float): 该 Tap 被打击的时间。
            trace (int): 该 Tap 落在轨道的编号，以 1-4 中的一个整数表示。
        """
        super().__init__(touch_time, 1)
        self.trace = trace


class Hold(BaseNotes):
    """Hold Note 类
    """

    def __init__(self, start_time: float, end_time: float, trace: float) -> None:
        """该函数用来生成一个 Hold Note。

        Args:
            start_time (float): 该 Hold 被开始打击的时间
            end_time (float): 该 Hold 被结束打击的时间
            trace (int): 该 Hold 落在轨道的编号。以 1-4 中的一个整数表示。
        """
        super().__init__(start_time, 2)
        self.end_time, self.trace = end_time, trace


class SkyNote(BaseNotes):
    """Sky Note 类
    """

    def __init__(self, touch_time: float, x_position: float, y_position: float) -> None:
        """该函数用来生成一个 Sky Note。

        Args:
            touch_time (float): 该 Sky Note 被打击的时间
            x_position (float): 该 Sky Note 被打击时落在的位置（将由 get_sn_position 函数计算）
            y_position (float): 该 Sky Note 被打击时落在的位置（将由 get_sn_position 函数计算）
        """
        super().__init__(touch_time, 3)
        self.x_position, self.y_position = x_position, y_position


class Arc(BaseNotes):
    """Arc Note 类
    """

    def __init__(
        self, start_time: float, end_time: float, x_start_pos: float, y_start_pos: float,
        x_end_pos: float, y_end_pos: float, arc_color: int, none_value: str, is_trace: bool
    ) -> None:
        """该函数用来生成一个 Arc Note。

        Args:
            start_time (float): 该 Arc 被开始打击的时间。
            end_time (float): 该 Arc 被结束打击的时间。
            x_start_pos (float): 该 Arc 被开始打击时的横向位置（0-1 之间的浮点数）
            y_start_pos (float): 该 Arc 被结束打击时的纵向位置（0-1 之间的浮点数）
            x_end_pos (float): 该 Arc 被结束打击时的横向位置（0-1 之间的浮点数）
            y_end_pos (float): 该 Arc 被结束打击时的纵向位置（0-1 之间的浮点数）
            arc_color (int): 该 Arc 的颜色（0 为蓝色，1 为红色，2 为绿色）
            none_value (str): 该 Arc 的 NONE 值。
            is_trace (bool): 该 Arc 是否为黑线。
        """
        super().__init__(start_time, 4)
        self.end_time, self.x_start_pos, self.y_start_pos, self.x_end_pos, self.y_end_pos, \
            self.arc_color, self.none_value, self.is_trace = end_time, x_start_pos, y_start_pos, \
                x_end_pos, y_end_pos, arc_color, \
            none_value, is_trace


class TimingGroup:
    """Timing Group 类
    """
    def __init__(self, tg_num: int, bpm_list: list):
        """该函数用来实例化一个 TimingGroup。

        Args:
            tg_num (int): 该 TimingGroup 在全谱面的编号。
            bpm_list (list): 该 TimingGroup 内 BPM 的变化列表。
        """
        self.tg_num = tg_num
        self.bpm_list = bpm_list
