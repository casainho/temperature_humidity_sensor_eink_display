#!/bin/bash
cd test
python -m coverage run -m unittest discover
#python -m coverage report