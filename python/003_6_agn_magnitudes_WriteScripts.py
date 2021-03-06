"""
export GIT_AGN_MOCK='/home/comparat/software/lss_mock_dev/'
export GIT_XPAINT='/home/comparat/software/XSB_Painting'


import os, sys
import glob
import numpy as n

scripts = n.array(glob.glob("MD10_sat*.sh"))
scripts.sort()

for script in scripts[::-1]:
  os.system('sbatch '+script)


"""

import time
import sys
import os
from os.path import join
import glob
import numpy as n

lss_git_dir = os.path.join(os.environ['GIT_AGN_MOCK'], 'python')
run_dir = os.path.join(lss_git_dir, '003_6_log')


def writeScript(env, ftyp):
	min_ = 0 
	max_ = 768
	bds = n.arange(min_, max_+14, 14)
	for ii, (min_X, max_X) in enumerate(zip(bds[:-1], bds[1:])):
		#f = open(os.path.join(run_dir, env + '_' + ftyp + '_' + hpx+ ".sh"), 'w')
		f = open(os.path.join(run_dir, env + '_' + ftyp + '_' + str(ii).zfill(2) + ".sh"), 'w')
		f.write("#!/bin/bash \n")
		f.write("#SBATCH --time=2000:00:00 \n")
		f.write("#SBATCH --nodes=1 \n")
		f.write("#SBATCH --ntasks=1 \n")
		f.write("#SBATCH --cpus-per-task=1 \n")
		f.write("#SBATCH --job-name=" + env + '_' + ftyp + " \n")
		f.write(" \n")
		f.write(". /home_local/4FSOpsim/py36he2srv/bin/activate \n")
		f.write("export OMP_NUM_THREADS=1 \n")
		f.write(" \n")
		f.write("cd " + lss_git_dir + " \n")
		f.write(" \n")
		for jj in n.arange(min_X, n.min([max_X, max_]), 1):
			f.write("python3 003_6_agn_magnitudes.py "+env + ' ' +ftyp+ ' ' + str(int(jj))+" \n")
		f.write(" \n")
		f.close()


t0 = time.time()

env = 'MD10'
writeScript(env, 'all')#, str(int(jj)))
env = 'MD04'
writeScript(env, 'all')#, str(int(jj)))
env = 'UNIT_fA1_DIR'
writeScript(env, 'all')#, str(int(jj)))
env = 'UNIT_fA2_DIR'
writeScript(env, 'all')#, str(int(jj)))
env = 'UNIT_fA1i_DIR'
writeScript(env, 'all')#, str(int(jj)))
	#writeScript(env, 'sat')#, str(int(jj)))
