#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 347 
python ../pre-process-esass.py 347 
python ../esass.py 347 
