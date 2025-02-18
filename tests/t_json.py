import json
import orjson
import os.path
from argparse import ArgumentParser

from cotests import bench_batch


"""
$ python -m tests.t_json /path/to/your/file.json
"""


def bench_json(file_path: str):
    with open(file_path, 'r') as f:
        json.load(f)

def bench_json_rb(file_path: str):
    with open(file_path, 'rb') as f:
        json.load(f)

def bench_orjson(file_path: str):
    with open(file_path, 'rb') as f:
        orjson.loads(*f)

def bench_orjson2(file_path: str):
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
        bench_json_rb,
        bench_orjson,
        bench_orjson2,
        iterations=50,
        global_args={args.path_file},
        global_kwargs={'file_path': args.path_file},
        raise_exceptions=True,
    )

"""
+---------------------------------------------------------------------------+
|    full    |    max     |    min     |    avg     |       f       |   %   |
| 11.901 sec | 268.898 ms | 214.831 ms | 238.022 ms | bench_json    | 154.3 |
| 11.729 sec | 274.584 ms | 213.716 ms | 234.575 ms | bench_json_rb | 152.1 |
|  8.575 sec | 193.270 ms | 161.842 ms | 171.504 ms | bench_orjson  | 111.2 |
|  7.713 sec | 172.493 ms | 145.525 ms | 154.252 ms | bench_orjson2 | 100.0 |
+---------------------------------------------------------------------------+

"""