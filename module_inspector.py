import csv
from itertools import repeat, imap
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


def write_to_csv(target_file, filename_dependencies):
    with open(target_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'dependencies'])
        for filename, dependencies in filename_dependencies:
            writer.writerow([filename] + list(dependencies))


def csv_to_dict(target_file):
    with open(target_file) as f:
        return {row[0]: row[1:] for row in csv.reader(f)}


if __name__ == '__main__':
    project_dir = os.path.expanduser(sys.argv[1])
    all_imports = get_all_dependencies_in_project(project_dir)
    write_to_csv(sys.argv[2], all_imports)
