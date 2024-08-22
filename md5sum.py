#!/usr/bin/env python
"""Serve as a convenient md5sum command on windows."""
import argparse
import glob
import hashlib
import os
import sys

CHUNK_SIZE = 4096  # Process 4kb at a time
INVALID_FILES = {'.', '..'}  # Ignore these
HASH_CHARS = {'a', 'b', 'c', 'd', 'e', 'f',
              '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}


def eprint(*args, **kwargs):
    """Print wrapper for stderr."""
    print(*args, file=sys.stderr, **kwargs)


def calculate_md5sum(file_path):
    """
    Calculate the md5sum for the given file.

    @param file_path: path to the file
    @return string of the md5sum, or None if unsuccessful
    """
    md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as file_path:
            chunk = file_path.read(CHUNK_SIZE)
            while chunk:
                md5.update(chunk)
                chunk = file_path.read(CHUNK_SIZE)
    except FileNotFoundError:
        return None
    return md5.hexdigest()


def print_line(md5, file_path):
    """
    Print a line of an md5 in the format of linux md5 files.

    @param md5: string of the md5sum for the file
    @param file_path: path to the file as it was input to the script
    """
    print('{}  {}'.format(md5, file_path))


def add_files_recursive(targets, root_dir):
    """
    Recursively add files to the list of targets.

    @param targets: list of target files to add to
    @param root_dir: directory to begin recursive search
    """
    for path, directories, files in os.walk(root_dir):
        for f in files:
            targets.append(os.path.join(path, f))


def check_md5(md5_file):
    """
    Verify all of the file hashes.

    @param md5_file: md5 containing all hashes in format:
    <hash>  <file>
    <hash>  <file>
    ...
    """
    # Load all files and their hashes
    targets = []
    n_bad = 0  # Number of invalid options for hashes
    with open(md5_file, 'r') as input_file:

        for line in input_file.readlines():
            line = line.strip()
            if len(line) <= 0:
                continue

            # Verify components of line
            line_l = line.split()
            md5_hash = line_l[0].lower()
            target = line_l[1]

            if len(md5_hash) != 32:
                eprint('invalid line: {}'.format(line))
                continue
            for c in md5_hash:
                if c not in HASH_CHARS:
                    eprint('invalid hash: {}'.format(line))
                    continue
            if len(target) <= 0:
                eprint('invalid line: {}'.format(line))
                continue

            targets.append((md5_hash, target))

    # Calculate hashes
    for target in targets:
        target_hash = calculate_md5sum(target[1])
        if target_hash is not None and target_hash == target[0]:
            print('{}: OK'.format(target[1]))
        else:
            print('{}: FAIL'.format(target[1]))
            n_bad += 1

    # Print final feedback and get correct exit code
    if n_bad > 0:
        eprint('{} files failed to pass hash check'.format(n_bad))
        sys.exit(1)


def parse_args():
    """
    Parse command line args.

    If -h or --help is used, this will exit early. Otherwise,
    this creates a list of files of which to calculate the md5sum.
    @return list of file paths of which to create md5sum hashes
    """
    # First parse arguments
    parser = argparse.ArgumentParser(
        'Calculates md5sum hashes for input files.')
    parser.add_argument('files',
                        nargs='*',
                        help='files to calculate md5sums for.')
    parser.add_argument('-r', dest='recursive', action='store_true',
                        default=False, help='recurse into directories')
    parser.add_argument('-c', dest='check', type=str, default=None,
                        help='check the hashes using an md5 file')
    args = parser.parse_args()

    # If used with check arg, check and then exit
    if args.check is not None:
        check_md5(args.check)
        exit()

    # Now create list of files. If there are globs, we perform
    # glob expansion here
    files = []
    for f in args.files:

        globs = glob.glob(f)
        if len(globs) == 0:
            files.append(f)  # Let this propogate to be handled later

        for file_path in globs:

            # Skip invalid captures from glob
            if file_path in INVALID_FILES:
                continue

            # Recurse into directories if recursive. Otherwise, skip
            if os.path.isdir(file_path):
                if args.recursive:
                    add_files_recursive(files, file_path)
            else:
                files.append(file_path)
    return files


def main():
    """Follow main flow."""
    # Determine targets
    files = parse_args()

    # Calculate hashes
    errors = []
    md5s = []  # Tuples of (hash, file) for successful hashes
    for f in files:
        md5 = calculate_md5sum(f)
        if md5 is None:
            errors.append(f)
            continue
        md5s.append((md5, f))

    # Print hashes
    for calculation in md5s:
        print_line(calculation[0], calculation[1])

    # Calculate errors
    if len(errors) > 0:
        eprint('\nERROR: unable to calculate {} hashes'.format(len(errors)))
        for err in errors:
            eprint('\t{}'.format(err))


if __name__ == '__main__':
    main()