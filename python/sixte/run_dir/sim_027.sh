#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 027 
python ../pre-process-esass.py 027 
python ../esass.py 027 
