#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 592 
python ../pre-process-esass.py 592 
python ../esass.py 592 
