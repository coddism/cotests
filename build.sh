pip install -U build twine
python3 -m build
python3 -m twine upload --repository testpypi dist/*
#python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps cotests

#twine upload dist/*
#pip install cotests
