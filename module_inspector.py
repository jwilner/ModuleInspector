import csv
import os
import sys
from functools import partial

from path_analysis import get_all_files, is_python_source_file, \
    find_module_path
from import_readers import find_dependencies


def get_all_dependencies_in_project(directory):
    path_finder = partial(find_module_path, directory)
    for python_file in get_all_files(directory, is_python_source_file):
        yield python_file, list(find_dependencies(python_file, path_finder))


def write_to_csv(target_file, filename_dependencies):
    with open(target_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'dependencies'])
        for filename, dependencies in filename_dependencies:
            writer.writerow([filename] + list(dependencies))


def csv_to_dict(target_file):
    with open(target_file) as f:
        return {row[0]: row[1:]
                for row in csv.reader(f)}


if __name__ == '__main__':
    project_dir = os.path.expanduser(sys.argv[1])
    all_imports = get_all_dependencies_in_project(project_dir)
    write_to_csv(sys.argv[2], all_imports)
