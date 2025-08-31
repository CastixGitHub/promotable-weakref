set -e

rm -rf venv dist build

python -m build --no-isolation

virtualenv venv
. venv/bin/activate

pip install dist/promotable_weakref-0.0.1-cp313-cp313-linux_x86_64.whl

python test.py
