import json
import orjson
import os.path
from argparse import ArgumentParser

from cotests import bench_batch


"""
$ python -m tests.t_json /path/to/your/file.json
"""


__FILE_RES_LEN = 140197


def bench_json(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)
        assert len(data) == __FILE_RES_LEN
        # print(len(data))

def bench_json_rb(file_path: str):
    with open(file_path, 'rb') as f:
        data = json.load(f)
        assert len(data) == __FILE_RES_LEN
        # print(len(data))

def bench_orjson(file_path: str):
    with open(file_path, 'rb') as f:
        data = orjson.loads(*f)
        assert len(data) == __FILE_RES_LEN
        # print(len(data))


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
        iterations=3,
        with_args=(args.path_file,),
        # with_kwargs={'file_path': args.path_file},
    )
