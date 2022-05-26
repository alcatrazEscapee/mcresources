#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

# This is a profile of different file I/O methods, in order to both maximize performance and minimize unnecessary file writes
# Run with python -m cProfile file_io_benchmark.py
# Variables: JSON size and complexity, File Match / Equal Percent


import json
import os
import random


def benchmark_always_overwrite(f, data):
    with open(f, 'w') as file:
        json.dump(data, file, indent=2)


def benchmark_overwrite_if_different(f, data):
    text = json.dumps(data, indent=2)
    if os.path.isfile(f):
        with open(f, 'r') as file:
            old_text = file.read()
        if old_text == text:
            return
    with open(f, 'w') as file:
        file.write(text)


def benchmark_overwrite_if_json_different(f, data):
    if os.path.isfile(f):
        with open(f, 'r') as file:
            old_data = json.load(file)
        if old_data == data:
            return
    with open(f, 'w') as file:
        json.dump(data, file, indent=2)


def main():
    f = '../../sample/generated/benchmark.json'

    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, 'w') as file:
        json.dump({}, file, indent=2)

    for _ in range(10_000):
        data = dict(('key_' + str(k), 'value_' + str(random.randint(1, 100))) for k in range(10))
        benchmark_always_overwrite(f, data)
        data = dict(('key_' + str(k), 'value_' + str(random.randint(1, 100))) for k in range(10))
        benchmark_overwrite_if_different(f, data)
        data = dict(('key_' + str(k), 'value_' + str(random.randint(1, 100))) for k in range(10))
        benchmark_overwrite_if_json_different(f, data)


if __name__ == '__main__':
    main()
