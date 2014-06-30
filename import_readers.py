from itertools import imap
from functools import partial
import re

FROM_IMPORT = re.compile(r"""
                         ^from\s+
                         ([\w\.]+)\s+
                         import\s+
                         \(?\s*
                         ([\w\.]+(?:\s*,\s*[\w\.]+)*)
                         """, re.VERBOSE)


GENERAL_IMPORT = re.compile(r"""
                            ^import\s+
                            \(?\s*
                            ([\w\.]+(?:\s*,\s*[\w\.]+)*)
                            """, re.VERBOSE)


def find_dependencies(full_path, path_finder):
    local_path_finder = partial(path_finder, full_path)
    with open(full_path) as f:
        for line in _join_lines(f):
            for reader in find_general_imports, find_from_imports:
                for imported in reader(line, local_path_finder):
                    yield imported


def _join_lines(lines):
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


def find_general_imports(line, path_finder):
    match = GENERAL_IMPORT.search(line)
    if match is None:
        raise StopIteration()

    for imp in imap(str.strip, match.group(1).split(',')):
        path = path_finder(imp)
        if path is not None:
            yield path


def find_from_imports(line, path_finder):
    match = FROM_IMPORT.search(line)
    if match is None:
        raise StopIteration()

    unqualified_name = match.group(1)
    following_parts = imap(str.strip, match.group(2).split(','))
    yielded_unqualified_name = False

    for imp in following_parts:
        fully_qualified = "%s.%s" % (unqualified_name, imp)
        path = path_finder(fully_qualified)

        if path is not None:
            yield path
        elif not yielded_unqualified_name:
            # if we can't find the part on the right
            # we need to find the left part
            path = path_finder(unqualified_name)
            if path is not None:
                yield path
                yielded_unqualified_name = True
