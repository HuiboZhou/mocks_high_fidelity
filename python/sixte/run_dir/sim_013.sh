#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 013 
python ../pre-process-esass.py 013 
python ../esass.py 013 
