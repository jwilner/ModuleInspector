from itertools import imap, chain
import re

IMPORT_REGEX = re.compile(r"""(?:from\s([\w\.]+)\simport\s.+)|
                              (?:import\s([\w\.]+)\sas.+)|
                              (?:import(?:\s([\w\.,\s]+)?))""",
                          re.VERBOSE)


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
    lines = imap(str.rstrip, lines)

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
    with open(full_path) as f:
        for imported in _flat_map(parse_line, join_lines(f)):
            yield imported


def _flat_map(f, *args):
    return chain.from_iterable(imap(f, *args))
