#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 010 
python ../pre-process-esass.py 010 
python ../esass.py 010 
