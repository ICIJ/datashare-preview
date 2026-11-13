import unittest

from dspreview.preview import get_size_height


class PreviewTest(unittest.TestCase):

    def test_numeric_size_is_capped_to_the_largest_size(self):
        self.assertEqual(get_size_height('100000'), 960)

    def test_numeric_size_below_the_cap_is_kept(self):
        self.assertEqual(get_size_height('200'), 200)
