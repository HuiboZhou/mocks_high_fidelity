#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 200 
python ../pre-process-esass.py 200 
python ../esass.py 200 
