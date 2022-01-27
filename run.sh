#!/usr/bin/env bash

DAMASK_grid -l tensionX.yaml -g onephase.vti
#DAMASK_grid -l tensionX.yaml -g simple.vti -r 120 # normal restart (should work)
./regridding.py
DAMASK_grid -l tensionX.yaml -g onephase-rg.vti -r 120 # normal restart (should work)
