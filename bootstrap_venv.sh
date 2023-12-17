# Needed for Toolforge nowadays
# Run as toolforge jobs run bootstrap-venv --command "cd $PWD && ./bootstrap_venv.sh" --image python3.11 --wait
#!/bin/bash

# use bash strict mode
set -euo pipefail

# delete the venv, if it already exists
rm -rf venv

# create the venv
python3 -m venv venv

# activate it
source venv/bin/activate

# upgrade pip inside the venv and add support for the wheel package format
pip3 install -U pip pymysql

# Change the following section depending on what your tool needs!

# install some concrete packages
# pip install requests
# pip install pyyaml

# or, install all packages from src/requirements.txt
# pip install -r src/requirements.txt
