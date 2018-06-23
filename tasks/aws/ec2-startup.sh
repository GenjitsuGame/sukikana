#!/bin/bash

yum update -y
yum install -y python36

git clone https://github.com/GenjitsuGame/sukikana.git

pip-3.6 install -r sukikana/tasks/requirements.txt