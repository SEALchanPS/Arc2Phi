import os

from assets import *


class ArcChart:
    pass


class TimingGroup:
    def __init__(self, tg_num: int, lines_list: list[str]):
        self.bpmListLine = []
        self.bpmListDict = {}
        self.TapList = []
        self.tg_num = tg_num
        print(f"已加载 Arcaea 谱面文件中第 {self.tg_num} 个 Timing Group。正在对其进行分析……")
        line_num = 0
        for line in lines_list:
            if line.startswith("timing"):
                self.bpmListLine.append(line)
            else:
                pass
        for line in self.bpmListLine:
            one_line_bpm_info = line.replace("(", "").replace(")", "").replace("timing", "").split(",")
            self.bpmListDict[one_line_bpm_info[0]] = one_line_bpm_info[1]
        for line in lines_list:
            line_num += 1
            print(f"正在分析行 {line_num} 内容为 {line}……")

            # 以下内容正在等待重构
            if line.startswith("AudioOffset"):
                offset_value = line.replace("AudioOffset:", "")
                self.offset = offset_value
                self.set_offset(offset_value)
            # 以上内容正在等待重构

            elif line.startswith("("):
                self.tap(line)
            elif line.startswith("arc"):
                self.arc(line)
            elif line.startswith("hold"):
                self.hold(line)

            else:
                raise ArcChartException(f"在谱面第 {tg_num} 个 Timing Group 中，第 {line_num} 个 Note 无法被识别：{line}")

        if not self.offset:
            self.offset = 0
            self.set_offset(0)

    def set_offset(self, offset):
        self.offset = offset
        if os.path.exists("base_info_offset.txt"):
            os.remove("base_info_offset.txt")
        with open('base_info_offset.txt', 'x', encoding="utf-8") as offset_file:
            offset_file.write(offset)

    def arc(self, line: str):
        pass

    def tap(self, line: str):
        tap_info = line.replace("(", "").replace(")", "").split(",")
        self.TapList.append(Tap(float(tap_info[0]), int(tap_info[1]), self.bpmListDict))

    def hold(self, line: str):
        pass
