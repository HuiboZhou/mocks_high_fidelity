#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 420 
python ../pre-process-esass.py 420 
python ../esass.py 420 
