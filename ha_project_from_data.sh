#!/bin/bash

data_py=$(sed '1,/API/d' "data.py")

echo $data_py
