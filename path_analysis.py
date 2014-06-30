from collections import OrderedDict
from itertools import imap, repeat
import os
import re
import sys

PYTHON_EXT_REGEX = re.compile(r"(?:\.py$)|(?:\.so$)")
BUILT_IN = 1


def find_module_path(project_root, current_path, fully_qualified_name):
    if fully_qualified_name in sys.builtin_module_names:
        return BUILT_IN

    directories = remove_duplicates_in_order([os.path.dirname(current_path),
                                              project_root] + sys.path)
    for directory in directories:
        path = _find_module_in_directory(directory, fully_qualified_name)
        if path is not None:
            return path


def _find_module_in_directory(directory, fully_qualified_name):
    path = directory
    parts = fully_qualified_name.split('.')
    for part in parts[:-1]:
        path = os.path.join(path, part)
        if not is_path_to_python_module(path):
            return None

    final_paths = [os.path.join(path, "%s.py" % parts[-1]),
                   os.path.join(path, '%s.so' % parts[-1]),
                   os.path.join(path, parts[-1], '__init__.py')]

    return next((p for p in final_paths if os.path.exists(p)),
                None)


def get_all_files(directory, predicate):
    for dirname, _, filenames in os.walk(os.path.abspath(directory)):
        for full_path in imap(os.path.join, repeat(dirname), filenames):
            if predicate(full_path):
                yield full_path


def is_path_to_python_module(filename):
    try:
        return PYTHON_EXT_REGEX.search(filename) \
            or os.path.exists(os.path.join(filename, '__init__.py'))
    except OSError:
        return False


def is_python_source_file(filepath):
    return filepath.endswith('.py')


def remove_duplicates_in_order(some_list):
    return list(OrderedDict.fromkeys(some_list))