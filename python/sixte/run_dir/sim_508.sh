#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 508 
python ../pre-process-esass.py 508 
python ../esass.py 508 
