#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 191 
python ../pre-process-esass.py 191 
python ../esass.py 191 
