from collections import defaultdict
import json
from itertools import repeat, imap, count
import os
import sys
from functools import partial

from path_analysis import find_module_path
from import_readers import find_dependencies


def get_all_dependencies_in_project(directory):
    path_finder = partial(find_module_path, directory)
    for dirname, _, filenames in os.walk(os.path.abspath(directory)):
        for full_path in imap(os.path.join, repeat(dirname), filenames):
            if full_path.endswith('.py'):
                yield full_path, find_dependencies(full_path, path_finder)


def dump(target_file, filename_dependencies):
    ids = defaultdict(partial(next, count()))

    structure = {ids[fname]: [ids[d] for d in deps]
                 for fname, deps in filename_dependencies}

    filenames = [fname for fname, _ in sorted(ids.items(), key=lambda x:x[1])]

    with open(target_file, 'w') as f:
        json.dump({'filenames': filenames, 'structure': structure}, f)


def load_file(target_file):
    with open(target_file) as f:
        info = json.load(f)
    filenames = info['filenames']
    structure = info['structure']
    return filenames, structure


def get_good_names(filenames):
    short_name_to_name = {}

    def is_good_name(filename):
        return filename not in {'__init__.py', 'test'} and \
            filename not in short_name_to_name

    def get_good_name(full_name):
        remaining, basename = os.path.split(full_name)

        if is_good_name(basename):
            name = basename
        else:
            name = remaining
            while not is_good_name(name):
                remaining, name = os.path.split(remaining)
            if not name:
                name = full_name
        short_name_to_name[name] = full_name
        return name

    return map(get_good_name, filenames), short_name_to_name






if __name__ == '__main__':
    project_dir = os.path.expanduser(sys.argv[1])
    all_imports = get_all_dependencies_in_project(project_dir)
    write_to_csv(sys.argv[2], all_imports)
