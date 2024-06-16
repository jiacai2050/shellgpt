from shellgpt.utils.common import extract_code, prepare_prompt
from shellgpt.utils.conf import DEFAULT_IMAGE_DIR
from os import path
import unittest


class TestCommon(unittest.TestCase):
    def test_prepare_prompt(self):
        for args, expected in [
            ('hello', ('hello', [])),
            ('https://liujiacai.net/', ('https://liujiacai.net/', [])),
            ('//', ('//', [])),
            ('hello @@test.png', ('hello', [path.join(DEFAULT_IMAGE_DIR, 'test.png')])),
            ('hello /tmp/test.png', ('hello', ['/tmp/test.png'])),
            ('hello/tmp/te\nst.png', ('hello/tmp/te\nst.png', [])),
            ('hello/tmp/test.png', ('hello/tmp/test.png', [])),
            ('hello@@test.png', ('hello@@test.png', [])),
        ]:
            self.assertEqual(prepare_prompt(args), expected)

    def test_extract_code(self):
        for args, expected in [
            ('1+1', None),
            (
                """
            ```
            1+1
            ```
            """,
                '1+1',
            ),
            (
                """
            ```python
            1+1
            ```
            """,
                '1+1',
            ),
        ]:
            self.assertEqual(extract_code(args), expected)
