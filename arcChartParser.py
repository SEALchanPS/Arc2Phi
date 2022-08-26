"""该模块用来解析 Arcaea 谱面。
"""
import os

from assets import *

timing_group_list = []


class ArcChart:
    """该类用来创建 Arcaea 谱面实例，以供解析。
    """

    def __init__(self, file_lines: list):
        self.file_lines = file_lines
        line_num = 0
        self.last_end_line_num = 0
        self.timing_group_value_dict = {}
        got_timing_group_0 = False
        for line in self.file_lines:
            line_num += 1
            if line.startswith("AudioOffset"):
                offset_value = line.replace("AudioOffset:", "")
                self.offset = offset_value
                self.set_offset(offset_value)
                self.last_start_line_num = line_num
            elif line.startswith("-"):
                self.last_start_line_num = line_num
            elif line.startswith("timinggroup()"):
                if not self.last_end_line_num == 0:
                    raise ArcChartException(
                        f"解析谱面文件的第 {line_num} 行时发生未知错误。它最有可能的触发原因是一个位于 {self.last_start_line_num} - {self.last_end_line_num} 的 Timing Group 未完全闭合导致的。")
                if not got_timing_group_0:
                    self.last_end_line_num = line_num - 1
                    self.timing_group_value_dict[self.last_start_line_num] = self.last_end_line_num
                    print(
                        f"解析谱面文件的第 {line_num} 行时找到了 Timing Group 的开始标志。已经界定 Timing Group 0 的范围。")
                    self.this_start_line_num = line_num
                    got_timing_group_0 = True
                elif got_timing_group_0:
                    self.this_start_line_num = line_num
            elif line.startswith("}"):
                self.this_end_line_num = line_num
                if not self.this_start_line_num:
                    raise ArcChartException(
                        f"解析谱面文件的第 {line_num} 时发现了一个 Timing Group 的结束标志，但是并未找到开始标志。")
                else:
                    self.timing_group_value_dict[self.this_start_line_num] = self.this_end_line_num
                self.last_start_line_num = self.this_start_line_num
                self.last_end_line_num = self.this_end_line_num
                self.this_end_line_num = 0
                self.this_start_line_num = 0
        if not got_timing_group_0:
            self.timing_group_value_dict[self.last_start_line_num + 1] = len(self.file_lines)
            self.this_start_line_num, self.this_end_line_num = 0, 0
        if self.this_end_line_num != 0 or self.this_start_line_num != 0:
            raise ArcChartException(
                f"在对该谱面的 Timing Group 进行拆分时发生了未知错误，它最有可能的触发原因是一个开始行为 {self.this_start_line_num} 的Timing Group 没有结束标志。")
        global timing_group_list
        timing_group_num = 0
        timing_group_list = []
        for single_timing_group in self.timing_group_value_dict.items():
            timing_group_num += 1
            this_group_chart_start_line = single_timing_group[0]
            this_group_chart_end_line = single_timing_group[1]
            this_group_chart_lines = self.file_lines[this_group_chart_start_line: this_group_chart_end_line]
            timing_group_list.append(TimingGroup(
                timing_group_num, this_group_chart_lines))

        # 考虑没有 `AudioOffset` 的情况
        if not self.offset:
            self.offset = 0
            self.set_offset(0)

    def set_offset(self, offset):
        """该函数用来将设定的谱面音乐延迟写入配置文件。

        Args:
            offset (str): 谱面音乐延迟数值。本应为 float，但鉴于该值由文件读取且写入文件，故不做类型转换。
        """
        self.offset = offset
        if os.path.exists("base_info_offset.txt"):
            os.remove("base_info_offset.txt")
        with open('base_info_offset.txt', 'x', encoding="utf-8") as offset_file:
            offset_file.write(offset)


class TimingGroup:
    """该类用来创建 Timing Group 的实例。
    """

    def __init__(self, tg_num: int, chart_lines_list: list[str]):
        """该函数用来创建 Timing Group 的实例。

        Args:
            tg_num (int): 在该谱面中，Timing Group 的编号。
            chart_lines_list (list[str]): 该 Timing Group 包含的谱面文件行。

        Raises:
            ArcChartException: 当存在无法识别的 Note 时，抛出该异常。
        """

        # 初始化变量
        self.bpm_list_line = []
        self.bpm_list_dict = {}
        self.tap_list = []
        self.tg_num = tg_num

        # 报告日志
        print(f"已加载 Arcaea 谱面文件中第 {self.tg_num} 个 Timing Group。正在对其进行分析……")

        # 读取整个 Timing Group 中的 BPM 设定行
        line_num = 0
        for line in chart_lines_list:
            if line.startswith("timing"):
                self.bpm_list_line.append(line)
            else:
                pass

        # 将 BPM 设定行组成的列表重置为字典
        for line in self.bpm_list_line:
            one_line_bpm_info = line.replace("(", "").replace(
                ")", "").replace("timing", "").split(",")
            self.bpm_list_dict[one_line_bpm_info[0]] = one_line_bpm_info[1]

        # 按照顺序实例化对应谱面元素
        for line in chart_lines_list:
            line_num += 1
            print(f"正在分析行 {line_num} 内容为 {line}……")

            if line.startswith("("):
                self.tap(line)
            elif line.startswith("arc"):
                self.arc(line)
            elif line.startswith("hold"):
                self.hold(line)

            # 当遇到无法识别的 Note 类型时，抛出异常
            else:
                raise ArcChartException(
                    f"在谱面第 {tg_num} 个 Timing Group 中，第 {line_num} 个 Note 无法被识别：{line}")

    def arc(self, line: str):
        """该函数用来生成一个音弧的实例。

        Args:
            line (str): 该音弧在谱面文件中的相关行。
        """
        pass

    def tap(self, line: str):
        """该函数用来生成一个 Tap 的实例。

        Args:
            line (str): 该 Tap 在谱面文件中的相关行。
        """
        tap_info = line.replace("(", "").replace(")", "").split(",")
        self.tap_list.append(
            Tap(float(tap_info[0]), int(tap_info[1]), self.bpm_list_dict))

    def hold(self, line: str):
        """该函数用来生成一个 Hold 的实例。

        Args:
            line (str): 该 Hold 在谱面文件中的相关行。
        """
        pass
