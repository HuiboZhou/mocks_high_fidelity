#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 720 
python ../pre-process-esass.py 720 
python ../esass.py 720 
