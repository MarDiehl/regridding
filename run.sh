#!/usr/bin/env bash

DAMASK_grid -l ../tensionX.yaml -g simple.vti
#DAMASK_grid -l tensionX.yaml -g simple.vti -r 14 # normal restart (should work)
../regridding.py
DAMASK_grid -l ../tensionX.yaml -g simple-rg.vti -r 14 # normal restart (should work)
