#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 539 
python ../pre-process-esass.py 539 
python ../esass.py 539 
