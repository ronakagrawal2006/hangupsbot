#!/usr/bin/env bash
ENV="${ENV:-Local}"
python3 setup.py build
python3 setup.py install
ENV=$ENV hangupsbot