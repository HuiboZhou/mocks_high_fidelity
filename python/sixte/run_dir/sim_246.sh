#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 246 
python ../pre-process-esass.py 246 
python ../esass.py 246 
