#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 748 
python ../pre-process-esass.py 748 
python ../esass.py 748 
