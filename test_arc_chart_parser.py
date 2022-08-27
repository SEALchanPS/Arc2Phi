"""这个模块用来对 Arcaea 谱面解析器进行测试。
"""
import unittest
import random
from assets import *
from arcChartParser import *


class TestArcChartParser(unittest.TestCase):
    """该类用来对 Arcaea 谱面解析器做单元测试。
    """

    def test_if_trace_out_of_range(self):
        """该函数用来测试 Arcaea 谱面解析器是否会对越界的轨道编号抛出异常。
        """
        with self.assertRaises(ArcChartException):
            Tap(0, 5, {0: 0, 1: 1})
    
    def test_if_set_positive_offset_works(self):
        offset_is_given = random.randint(0, 5000)
        bytes_to_give = [f'AudioOffset: {offset_is_given}', '---', '(1,1)']
        ArcChart(bytes_to_give)
        with open('base_info_offset.txt', 'r', encoding='utf-8') as offset_file:
            offset_in_file = offset_file.read()
        self.assertEqual(int(offset_in_file), offset_is_given)

    def test_if_set_negative_offset_works(self):
        offset_is_given = random.randint(-5000, 0)
        bytes_to_give = [f'AudioOffset: {offset_is_given}', '---', '(1,1)']
        ArcChart(bytes_to_give)
        with open('base_info_offset.txt', 'r', encoding='utf-8') as offset_file:
            offset_in_file = offset_file.read()
        self.assertEqual(int(offset_in_file), offset_is_given)

    def test_create_timing_group_only_0(self):
        offset_is_given = random.randint(-5000, 0)
        bytes_to_give = [f'AudioOffset: {offset_is_given}', '---', 'timing(0,3)', '(1,1)', 'hold(2,3,4)']
        arcChart = ArcChart(bytes_to_give)
        with open("timing_group_list.txt", "rb") as tg_list_file:
            timing_group_list = pickle.load(tg_list_file)
        self.assertEqual(timing_group_list[0].tg_num, 0)
        self.assertEqual(timing_group_list[0].tap_list[0].trace, 1)


if __name__ == "__main__":
    unittest.main()
