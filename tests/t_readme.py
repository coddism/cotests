import os
from cotests import test_module


dir_path = os.path.dirname(os.path.realpath(__file__))
test_module(
    dir_path,
    file_prefix='readme_',
    ignore_files={'readme_json.py'},
)
