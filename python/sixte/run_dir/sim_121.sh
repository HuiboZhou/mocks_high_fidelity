#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 121 
python ../pre-process-esass.py 121 
python ../esass.py 121 
