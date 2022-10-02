"""这个模块用来对 Arcaea 谱面解析器进行测试。
"""
import random
import unittest

from arcaea.chartparser.__init__ import *


class TestArcChartParser(unittest.TestCase):
    """该类用来对 Arcaea 谱面解析器做单元测试。
    """

    def test_if_trace_out_of_range(self):
        """该函数用来测试 Arcaea 谱面解析器是否会对越界的轨道编号抛出异常。
        """
        with self.assertRaises(ArcChartException):
            Tap(0, 5, {0: 0, 1: 1})

    def test_if_set_positive_offset_works(self):
        """该函数用来测试 Arcaea 谱面解析器是否会对正的谱面音乐延迟进行处理。
        """
        offset_is_given = random.randint(0, 5000)
        bytes_to_give = [f'AudioOffset: {offset_is_given}', '---', '(1,1)']
        ArcChart(bytes_to_give)
        with open('../base_info_offset.txt', 'r', encoding='utf-8') as offset_file:
            offset_in_file = offset_file.read()
        self.assertEqual(int(offset_in_file), offset_is_given)

    def test_if_set_negative_offset_works(self):
        """该函数用来测试 Arcaea 谱面解析器是否会对负的谱面音乐延迟进行处理。
        """
        offset_is_given = random.randint(-5000, 0)
        bytes_to_give = [f'AudioOffset: {offset_is_given}', '---', '(1,1)']
        ArcChart(bytes_to_give)
        with open('../base_info_offset.txt', 'r', encoding='utf-8') as offset_file:
            offset_in_file = offset_file.read()
        self.assertEqual(int(offset_in_file), offset_is_given)

    def test_create_timing_group_only_0(self):
        """该函数用来测试 Arcaea 谱面解析器是否会对单独 1 个 Timing Group 正确解析。
        """
        offset_is_given = random.randint(-5000, 0)
        bytes_to_give = [f'AudioOffset: {offset_is_given}', '---', 'timing(0,3)', '(1,1)', 'hold(2,3,4)']
        ArcChart(bytes_to_give)
        with open("../../timing_group_list.txt", "rb") as tg_list_file:
            timing_group_list = pickle.load(tg_list_file)
        self.assertEqual(timing_group_list[0].tg_num, 0)
        self.assertEqual(timing_group_list[0].tap_list[0].trace, 1)

    def test_create_3_timing_group(self):
        """该函数用来测试 Arcaea 谱面解析器是否会对 3 个 Timing Group 正确解析。
        归纳可得，如果通过该测试，则应当能够处理多 Timing Group 谱面。
        """
        offset_is_given = random.randint(-5000, 0)
        bytes_to_give = [f'AudioOffset: {offset_is_given}', '---', 'timing(0,3)', '(1,1)', 'hold(2,3,4)',
                         'timinggroup(){', 'timing(114514,1919810)', '(2,2)', '}', 'timinggroup(){',
                         'timing(114514,1919810)', '(3,3)', '}']
        ArcChart(bytes_to_give)
        with open("timing_group_list.txt", "rb") as tg_list_file:
            timing_group_list = pickle.load(tg_list_file)
        self.assertEqual(timing_group_list[0].tg_num, 0)
        self.assertEqual(timing_group_list[0].tap_list[0].trace, 1)
        self.assertEqual(timing_group_list[1].tg_num, 1)
        self.assertEqual(timing_group_list[1].tap_list[0].trace, 2)
        self.assertEqual(timing_group_list[2].tg_num, 2)
        self.assertEqual(timing_group_list[2].tap_list[0].trace, 3)

    def test_if_it_can_get_initial_position(self):
        """该函数用来测试 Arcaea 谱面解析器能否获得正确的 Note 初始位置。
        """
        with open("song_total_time.txt", "w", encoding="utf-8") as total_time_file:
            total_time_file.write("2")
        test_note = NoteBase(1500, 1, {0:100, 1000:200})
        self.assertEqual(test_note.time_0_position, 200000 * 0.000001)


if __name__ == "__main__":
    unittest.main()
