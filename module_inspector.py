import csv
from itertools import imap, chain
import os
import re
import sys

IMPORT_REGEX = re.compile(r"""(?:^from\s([\w\.]+)\simport\s.+$)|
                              (?:^import\s([\w\.]+)\sas\s.+$)|
                              (?:^import(?:\s([\w\.,\s]+)$))""",
                          re.VERBOSE)

PYTHON_EXT_REGEX = re.compile(r"\.py$")


def parse_line(line):
    """
    @param: line
    @return: list of imports found on line
    """
    try:
        match = filter(None, IMPORT_REGEX.search(line).groups())[0]
    except (IndexError, AttributeError):
        return []
    return map(str.strip, match.split(','))


def join_lines(lines):
    """
    @param lines, list of strings
    @yields lines joined on '\'
    """
    lines = imap(str.strip, lines)

    previous_lines = []
    for line in lines:
        if line.endswith('\\'):
            previous_lines.append(line)
        elif previous_lines:
            yield ''.join(previous_line[:-1]
                          for previous_line in previous_lines) + line
            previous_lines = []
        else:
            yield line


def find_imports_in_file(full_path):
    """
    @param full_path: full path to a .py file
    @yields each import found in file
    """
    with open(full_path) as f:
        for imported in _flat_map(parse_line, join_lines(f)):
            yield imported


def _flat_map(f, *args):
    return chain.from_iterable(imap(f, *args))


def _get_all_files(directory):
    for dirname, _, filenames in os.walk(os.path.abspath(directory)):
        for filename in filenames:
            yield os.path.join(dirname, filename)


def get_all_imports_in_project(directory, predicate=PYTHON_EXT_REGEX.search):
    return {filename: list(find_imports_in_file(filename))
            for filename in (fname for fname in _get_all_files(directory)
                             if predicate(fname))}


def get_module_name_from_filename(full_path):
    base_name, poss_mod_name = os.path.split(full_path)
    if poss_mod_name == '__init__.py':
        base_name, poss_mod_name = os.path.split(base_name)

    module_name = PYTHON_EXT_REGEX.sub('', poss_mod_name)
    module_names = [module_name]

    while is_module_directory(base_name):
        base_name, outer_dir = os.path.split(base_name)
        qualified = "{module_dir}.{module_name}".format(module_dir=outer_dir,
                                                        module_name=module_name)
        module_names.append(qualified)

    return module_names


def is_module_directory(directory):
    return os.path.exists(os.path.join(directory, '__init__.py'))


def write_to_csv(target_file, directory, file_imports):
    with open(target_file, 'w') as f:
        writer = csv.writer(f)
        for filename, imports in file_imports.iteritems():
            writer.writerow([filename] +
                            get_module_name_from_filename(filename)
                            + imports)


if __name__ == '__main__':
    all_imports = get_all_imports_in_project(sys.argv[1])
    write_to_csv(sys.argv[2], sys.argv[1], all_imports)
