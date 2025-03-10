import json
import orjson
import os.path
from argparse import ArgumentParser

from cotests import bench_batch


"""
$ python -m tests.readme_json /path/to/your/file.json
"""


def bench_json(file_path: str):
    with open(file_path, 'rb') as f:
        json.load(f)

def bench_orjson(file_path: str):
    with open(file_path, 'rb') as f:
        orjson.loads(f.read())


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('path_file')
    args = parser.parse_args()

    if not os.path.isfile(args.path_file):
        raise FileNotFoundError

    bench_batch(
        bench_json,
        bench_orjson,
        iterations=50,
        global_args={args.path_file},
    )
