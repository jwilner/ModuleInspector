import os
import unittest
import shutil

import path_analysis as pa


class TestResolveModule(unittest.TestCase):
    paths = ['/tmp/my_package/china/__init__.py',
             '/tmp/my_package/china/india/__init__.py',
             '/tmp/my_package/china/japan.py',
             '/tmp/my_package/china/india/food.py',
             '/tmp/my_package/foo.py',
             '/tmp/my_package/foos/ball.py']

    @staticmethod
    def func(x, y):
        return pa.find_module_path('/tmp/my_package', x, y)

    def setUp(self):
        shutil.rmtree('/tmp/my_package')

        for path in self.paths:
            try:
                os.makedirs(os.path.dirname(path))
            except OSError:
                pass
            with open(path, 'w') as f:
                f.write('This is a test')

    def test_resolve_module(self):
        self.assertEquals('/tmp/my_package/foo.py',
                          self.func('/tmp/my_package/faker.py', 'foo'))

    def test_resolve_module_from_deeper(self):
        self.assertEquals('/tmp/my_package/foo.py',
                          self.func('/tmp/my_package/india/__init__.py', 'foo'))

    def test_resolve_builtin(self):
        self.assertEquals(pa.BUILT_IN_LABEL % 'sys',
                          self.func('/tmp/my_package/faker.py', 'sys'))

    def test_resolve_standard_lib(self):
        self.assertIsNotNone(self.func('/tmp/my_package/faker.py', 'itertools'))

    def test_easy_qualified(self):
        self.assertEquals('/tmp/my_package/china/japan.py',
                          self.func('/tmp/my_package/faker.py', 'china.japan'))


class TestResolveModule2(unittest.TestCase):
    @staticmethod
    def set_up_directory(paths):
        shutil.rmtree('/tmp/my_package')

        for path in paths:
            try:
                os.makedirs(os.path.dirname(path))
            except OSError:
                pass
            with open(path, 'w') as f:
                f.write('barbazpa')

    def test_simple_case(self):
        paths = ['/tmp/my_package/foo/__init__.py',
                 '/tmp/my_package/foo/bar/__init__.py',
                 '/tmp/my_package/foo/bar/baz.py']
        self.set_up_directory(paths)
        result = pa.find_module_path('/tmp/my_package',
                                     '/tmp/my_package/faker.py',
                                     'foo.bar.baz')
        self.assertEquals('/tmp/my_package/foo/bar/baz.py', result)

    def test_finds_none(self):
        paths = ['/tmp/my_package/foo/__init__.py',
                 '/tmp/my_package/foo/bar/__init__.py',
                 '/tmp/my_package/foo/bar/baz.py']
        self.set_up_directory(paths)
        os.remove('/tmp/my_package/foo/__init__.py')

        result = pa.find_module_path('/tmp/my_package',
                                     '/tmp/my_package/faker.py',
                                     'foo.bar.baz')

        self.assertEquals(None, result)  # because no foo/__init__.py

    def test_finds_none_still(self):
        paths = ['/tmp/my_package/foo/__init__.py',
                 '/tmp/my_package/foo/bar/__init__.py',
                 '/tmp/my_package/foo/bar/baz.py']
        self.set_up_directory(paths)
        os.remove('/tmp/my_package/foo/bar/__init__.py')

        result = pa.find_module_path('/tmp/my_package',
                                     '/tmp/my_package/faker.py',
                                     'foo.bar.baz')

        self.assertEquals(None, result)  # because no bar/__init__.py
