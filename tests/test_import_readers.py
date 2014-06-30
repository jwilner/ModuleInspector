from functools import partial
import os
import unittest
import shutil

import import_readers as ir
from path_analysis import find_module_path


class RegexpTest(unittest.TestCase):
    reg = None

    def assertRegexpGroups(self, text, expected_groups):
        groups = self.reg.search(text).groups()
        self.assertEqual(groups, expected_groups)


class TestFromImportRegex(RegexpTest):
    reg = ir.FROM_IMPORT

    def test_from_import(self):
        self.assertRegexpGroups('from china import bob',
                                ('china', 'bob'))

    def test_with_parens(self):
        self.assertRegexpGroups('from china import (bob, japan, egypt)',
                                ('china', 'bob, japan, egypt'))

    def test_periods_ok(self):
        self.assertRegexpGroups('from egypt import china.japan',
                                ('egypt', 'china.japan'))

    def test_periods_ok_in_first_part(self):
        self.assertRegexpGroups('from egypt.israel import china.japan',
                                ('egypt.israel', 'china.japan'))


class TestGeneralImportRegex(RegexpTest):
    reg = ir.GENERAL_IMPORT

    def test_single_import(self):
        self.assertRegexpGroups("import chinese_food", ('chinese_food',))

    def test_multi_import(self):
        self.assertRegexpGroups('import chinese_food, indian_food',
                                ('chinese_food, indian_food',))

    def test_parens_import(self):
        self.assertRegexpGroups('import (chinese_food, indian_food)',
                                ('chinese_food, indian_food',))

    def test_as_import(self):
        self.assertRegexpGroups('import chinese_food as se',
                                ('chinese_food',))

    def test_periods_ok(self):
        self.assertRegexpGroups('import china.japan',
                                ('china.japan',))

    def test_multi_periods(self):
        self.assertRegexpGroups('import (china.japan, egypt.israel)',
                                ('china.japan, egypt.israel',))


class TestJoinLines(unittest.TestCase):
    def test_single_line(self):
        self.assertEqual(next(ir._join_lines(['abcde abcde abcde'])),
                         'abcde abcde abcde')

    def test_joined_lines(self):
        self.assertEqual(next(ir._join_lines(['abcde abcde \\',
                                              'abcde'])),
                         'abcde abcde abcde')

    def test_multiple_complicated(self):
        self.assertEqual(list(ir._join_lines(['hi everyone',
                                              'abc abc \\ ',
                                              'abc abc \\ ',
                                              'abc',
                                              '123'])),
                         ['hi everyone', 'abc abc abc abc abc', '123'])


class TestFindDependencies(unittest.TestCase):
    dir = '/tmp/my_package'

    files = {'chinatown/india.py': 'import israel, istanbul',
             'chinatown/__init__.py': '',
             'israel.py': 'import istanbul',
             'france.py': 'from chinatown import india',
             'istanbul/__init__.py': 'import africa',
             'africa.py': 'from israel import france'}

    def setUp(self):
        shutil.rmtree(self.dir)
        for filename, string in self.files.items():
            path = os.path.join(self.dir, filename)
            try:
                os.makedirs(os.path.dirname(path))
            except OSError:
                pass
            with open(path, 'w') as f:
                f.write(string)

    def test_find_dependencies(self):
        path_finder = partial(find_module_path, '/tmp/my_package')
        result = list(ir.find_dependencies(os.path.join(self.dir, 'africa.py'),
                                           path_finder))
        self.assertIn('/tmp/my_package/israel.py', result)

    def test_find_hard_dependencies(self):
        path_finder = partial(find_module_path, '/tmp/my_package')
        path = os.path.join(self.dir, 'chinatown/india.py')
        result = list(ir.find_dependencies(path, path_finder))
        self.assertEquals(['/tmp/my_package/israel.py',
                           '/tmp/my_package/istanbul/__init__.py'],
                          result)

    def test_find_from_init(self):
        path_finder = partial(find_module_path, '/tmp/my_package')
        path = os.path.join(self.dir, 'istanbul/__init__.py')
        result = list(ir.find_dependencies(path, path_finder))
        self.assertEquals(['/tmp/my_package/africa.py'], result)

