"""这个模块用来对 Arcaea 谱面解析器进行测试。
"""
import unittest
import random
from assets import Tap, ArcChartException
from arcChartParser import TimingGroup


class TestArcChartParser(unittest.TestCase):
    """该类用来对 Arcaea 谱面解析器做单元测试。
    """

    def test_if_trace_out_of_range(self):
        """该函数用来测试 Arcaea 谱面解析器是否会对越界的轨道编号抛出异常。
        """
        with self.assertRaises(ArcChartException):
            Tap(0, 5)
    
    def test_if_set_positive_offset_works(self):
        offset_is_given = random.randint(0, 5000)
        bytes_to_give = f'AudioOffset: {offset_is_given}'
        TimingGroup([bytes_to_give])
        with open('base_info_offset.txt', 'r', encoding='utf-8') as offset_file:
            offset_in_file = offset_file.read()
        self.assertEqual(int(offset_in_file), offset_is_given)

    def test_if_set_negative_offset_works(self):
        offset_is_given = random.randint(-5000, 0)
        bytes_to_give = f'AudioOffset: {offset_is_given}'
        TimingGroup([bytes_to_give])
        with open('base_info_offset.txt', 'r', encoding='utf-8') as offset_file:
            offset_in_file = offset_file.read()
        self.assertEqual(int(offset_in_file), offset_is_given)

if __name__ == "__main__":
    unittest.main()
