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
        with_args=(args.path_file,),
        # with_kwargs={'file_path': args.path_file},
        raise_exceptions=True,
    )

"""
+-------------------------------------------------------------------+
|    full    |    max     |    min     |    avg     |       f       |
| 11.600 sec | 242.746 ms | 214.939 ms | 231.993 ms | bench_json    |
| 11.425 sec | 238.720 ms | 214.494 ms | 228.491 ms | bench_json_rb |
|  7.924 sec | 162.412 ms | 154.662 ms | 158.485 ms | bench_orjson  |
|  7.431 sec | 155.457 ms | 143.811 ms | 148.624 ms | bench_orjson2 |
+-------------------------------------------------------------------+
"""