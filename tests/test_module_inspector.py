import os
import unittest

from python.ModuleInspector import module_inspector as mi


class TestRegexes(unittest.TestCase):
    def test_from_import(self):
        self.assertEqual(mi.parse_line('from china import bob'), ['china'])

    def test_normal_import(self):
        self.assertEqual(mi.parse_line('import chinese_food'), ['chinese_food'])

    def test_as_import(self):
        self.assertEqual(mi.parse_line('import chinese_food as se'),
                         ['chinese_food'])

    def test_multi_import(self):
        self.assertEqual(mi.parse_line('import chinese_food, indian_food'),
                         ['chinese_food', 'indian_food'])


class TestJoinLines(unittest.TestCase):
    def test_single_line(self):
        self.assertEqual(next(mi.join_lines(['abcde abcde abcde'])),
                         'abcde abcde abcde')

    def test_joined_lines(self):
        self.assertEqual(next(mi.join_lines(['abcde abcde \\',
                                             'abcde'])),
                         'abcde abcde abcde')

    def test_multiple_complicated(self):
        self.assertEqual(list(mi.join_lines(['hi everyone',
                                             'abc abc \\ ',
                                             'abc abc \\ ',
                                             'abc',
                                             '123'])),
                         ['hi everyone', 'abc abc abc abc abc', '123'])


class TestFindImportsInFile(unittest.TestCase):

    file_path = '/tmp/abcdefgh'
    literal = """
from china import bob
import pandas as pd
import os.path as f

cry a little bit
love life
import india, \
    egypt, japan"""

    def setUp(self):
        with open(self.file_path, 'w') as f:
            f.write(self.literal)

    def tearDown(self):
        os.remove(self.file_path)

    def test_find_imports_in_file(self):
        imports = list(mi.find_imports_in_file(self.file_path))
        self.assertEqual(imports, ['china', 'pandas', 'os.path', 'india',
                                   'egypt', 'japan'])

