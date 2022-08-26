"""这个模块用来对 Arcaea 谱面解析器进行测试。
"""
import unittest
from assets import Tap, ArcChartException


class TestArcChartParser(unittest.TestCase):
    """该类用来对 Arcaea 谱面解析器做单元测试。
    """

    def test_if_trace_out_of_range(self):
        """该函数用来测试 Arcaea 谱面解析器是否会对越界的轨道编号抛出异常。
        """
        with self.assertRaises(ArcChartException):
            Tap(0, 5)


if __name__ == "__main__":
    unittest.main()
