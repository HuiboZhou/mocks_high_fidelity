#!/bin/bash 
source /home/erosita/sw/sass-setup.sh eSASSdevel 
python ../simulate.py 549 
python ../pre-process-esass.py 549 
python ../esass.py 549 
