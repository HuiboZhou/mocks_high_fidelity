#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 289 
python ../pre-process-esass.py 289 
python ../esass.py 289 
