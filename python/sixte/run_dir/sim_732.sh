#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 732 
python ../pre-process-esass.py 732 
python ../esass.py 732 
