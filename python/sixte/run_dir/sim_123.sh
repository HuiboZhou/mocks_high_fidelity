#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 123 
python ../pre-process-esass.py 123 
python ../esass.py 123 
