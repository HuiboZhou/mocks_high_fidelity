"""
Creates a fits catalog containing the 4FS input columns.

Create the ID array
remove unwanted column
check rulesets and templates names are correct

make a catalogue with r_eff, n_sersic, fraction_flux_observed

"""
import glob
import sys
from astropy_healpix import healpy
import os
from scipy.special import gammainc  # , gamma,  gammaincinv, gammaincc
from scipy.stats import scoreatpercentile
import pandas as pd  # external package
from scipy.special import erf
from astropy.coordinates import SkyCoord
import astropy.constants as cc
import astropy.io.fits as fits
from astropy.table import Table, Column
import astropy.units as u
import numpy as n
import extinction
print('CREATES 4FS FITS FILES')
print('------------------------------------------------')
print('------------------------------------------------')

# astropy

#from lib_model_agn import *
#option = sys.argv[1]
#option = 'SNR3'
#option = 'eRASS8'
#option = 'eRASS3'
area_per_cat = healpy.nside2pixarea(8, degrees=True)

env = sys.argv[1]

# simulation setup
if env == "MD10" or env == "MD04":
    from astropy.cosmology import FlatLambdaCDM
    import astropy.units as u
    cosmoMD = FlatLambdaCDM(
        H0=67.77 * u.km / u.s / u.Mpc,
        Om0=0.307115)  # , Ob0=0.048206)
    h = 0.6777
    L_box = 1000.0 / h
    cosmo = cosmoMD
if env == "UNIT_fA1_DIR" or env == "UNIT_fA1i_DIR" or env == "UNIT_fA2_DIR":
    from astropy.cosmology import FlatLambdaCDM
    import astropy.units as u
    cosmoUNIT = FlatLambdaCDM(H0=67.74 * u.km / u.s / u.Mpc, Om0=0.308900)
    h = 0.6774
    L_box = 1000.0 / h
    cosmo = cosmoUNIT

root_dir = os.path.join(os.environ[env])

path_2_parent_catalog = os.path.join(root_dir, env+'_eRO_CLU_GAL.fit')

path_2_clusterBCG   = os.path.join(root_dir, 'S5_BCG_4MOST.fit')
path_2_clusterBCG_sersic   = os.path.join(root_dir, 'S5_BCG_4MOST_sersic.fit')
path_2_clusterredGAL = os.path.join(root_dir, 'S5_CGAL_4MOST.fit')

sub_survey_names = n.array([ 'cluster_BCG', 'cluster_redGAL', 'filament_GAL'])

# reassigns templates correctly
z_all = n.hstack(( 0., n.arange(0.3, 3., 0.2), 3.5, 4.5, 6. ))
zmins = z_all[:-1]
zmaxs = z_all[1:]

# to select BCG and red gal :
hd_all = fits.open(path_2_parent_catalog)
# to get 300,000 over the full sky
eROSITA_CLUSTERS = (hd_all[1].data['HOST_CLUSTER_FX_soft'] > 10**(hd_all[1].data['HOST_flux_limit_eRASS8_pt']+0.4)) & ( abs(hd_all[1].data['g_lat']) > 10 ) 
#area = 34089.
#print('full sky |g_lat|>10, N, N/deg2 = ',len(hd_clu[eROSITA_CLUSTERS]), len(hd_clu[eROSITA_CLUSTERS])/area)

# hdu containing only the 300k - 400k clusters of interest : 
hd_clu = hd_all[1].data[eROSITA_CLUSTERS]


Nall=len(hd_clu['g_lat'])

# =============================
# =============================
# optically selected cluster sample
# apply richness limit
# BCG
# =============================
# =============================
area_b10 = 34089./2.
area_b15 = 30575./2.
area_b20 = 27143./2.
area = area_b10
area_ero = (abs(hd_clu['g_lat']) > 10) & (hd_clu['g_lon'] > 180) & (hd_clu['dec'] < 20)
#r_10 = (area_ero) & (hd_clu['comoving_distance_to_cluster_in_rvir'] == 0.) # &  (hd_clu['richness'] > 20)  
bcg = (area_ero) & (hd_clu['comoving_distance_to_cluster_in_rvir'] == 0.) # & (hd_clu['HALO_M200c'] > 2.5e14) 

print(len(hd_clu['redshift_R'][area_ero])/area, 'obj in area')
#print(len(hd_clu['redshift_R'][r_10])/area, 'richness>20 clusters')
print(len(hd_clu['redshift_R'][bcg]), len(hd_clu['redshift_R'][bcg])/area) #, 'clusters M200c>2.5e14')
#print(len(hd_clu['redshift_R'][bcg]), 'clusters')
#hd_clu['HALO_id'][bcg]
#hd_clu['HALO_host_id'][bcg]

# =============================
# =============================
# galaxy members
# =============================
# =============================
cgal = (area_ero) & ( hd_clu['galaxy_mag_r'] < 22.5) & (hd_clu['is_quiescent'])  # (hd_clu['richness'] > 40) & 
print(len(hd_clu['redshift_R'][cgal]), len(hd_clu['redshift_R'][cgal])/area, 'galaxies in optical clusters L>40')


sub_survey_names = n.array([ 'cluster_BCG', 'cluster_redGAL', 'filament_GAL'])
N_subsurvey = {'cluster_BCG':1, 'cluster_redGAL':2, 'filament_GAL':3}
priority_values = {'cluster_BCG':100, 'cluster_redGAL':99, 'filament_GAL':98}

def create_4most_catalogue(t_survey, subsurvey):
	"""
	Creates a 4MOST subsurvey catalogue for S5
	
	Writes fiber magnitudes to the Table
	
	t_survey : (astropy Table) simulated catalogue
	subsurvey : (string) sub survey name
	"""
	N_targets=len(t_survey)
	N_obj = len(t_survey)
	#  limit size of the string columns to the size of the longer string in the corresponding columns. 
	# 'NAME':str, max 256 char
	N1 = n.arange(len(t_survey['galactic_ebv']))
	id_list = N_subsurvey[subsurvey]*1e8 + N1
	NAME = n.array([ str(int(el)).zfill(11) for el in id_list ])
	t_survey.add_column(Column(name='NAME', data=NAME, unit=''))
	# 'RA':n.float64, 1D
	# 'DEC':n.float64, 1D
	# 'PMRA':n.float32, 1E
	# 'PMDEC':n.float32, 1E
	# 'EPOCH':n.float32, 1E
	PMRA = n.zeros(N_obj)
	t_survey.add_column(Column(name='RA', data=t_survey['ra'], unit='deg'))
	t_survey.add_column(Column(name='DEC', data=t_survey['dec'], unit='deg'))
	t_survey.add_column(Column(name='PMRA', data=PMRA, unit='mas/yr'))
	PMDEC = n.zeros(N_obj)
	t_survey.add_column(Column(name='PMDEC', data=PMDEC, unit='mas/yr'))
	EPOCH = n.ones(N_obj)*2000.
	t_survey.add_column(Column(name='EPOCH', data=EPOCH, unit='yr'))
	# 'RESOLUTION':n.int16, 1I
	RESOLUTION = n.ones(N_obj).astype('int')
	t_survey.add_column(Column(name='RESOLUTION', data=RESOLUTION, unit=''))
	# 'SUBSURVEY':str, max 256 char
	SUBSURVEY = n.ones(N_obj).astype('str')
	SUBSURVEY[:] = subsurvey
	t_survey.add_column(Column(name='SUBSURVEY', data=SUBSURVEY, unit=''))
	# 'PRIORITY':n.int16, 1I
	PRIORITY = n.zeros(N_obj).astype('int') + priority_values[subsurvey]
	t_survey.add_column(Column(name='PRIORITY', data=PRIORITY, unit=''))

	# EBV for templates
	ebv_1000 = (t_survey['galactic_ebv']*1000).astype('int')
	ebv_1_0 = ( ebv_1000 > 1000 ) 
	ebv_0_5 = ( ebv_1000 > 500 ) & ( ebv_1000 <= 1000 ) 
	ebv_0_4 = ( ebv_1000 > 400 ) & ( ebv_1000 <= 500 ) 
	ebv_0_3 = ( ebv_1000 > 300 ) & ( ebv_1000 <= 400 ) 
	ebv_0_2 = ( ebv_1000 > 200 ) & ( ebv_1000 <= 300 ) 
	ebv_0_1 = ( ebv_1000 > 100 ) & ( ebv_1000 <= 200 ) 
	ebv_0_0 = ( ebv_1000 <= 100 ) 
	z_name = lambda z0, z1 : "_zmin_"+str(int(10*z0)).zfill(2)+"_zmax_"+str(int(10*z1)).zfill(2)
	# templates
	template_names = n.zeros(N_obj).astype('U100')
	ruleset_array = n.zeros(N_obj).astype('str')
	# S8 BG or LRG

	if subsurvey == 'cluster_BCG' :
		ruleset_array[:] = "ClusBCG"
		
	if subsurvey == 'cluster_redGAL':
		ruleset_array[:] = "RedGAL"

	for z0,z1 in zip(zmins,zmaxs):
		zsel = (t_survey['redshift_R']>=z0) & (t_survey['redshift_R']<z1)
		if len(zsel.nonzero()[0])>0:
			#ruleset_array[zsel] = "COSMO_RedGAL"
			template_names[(zsel)]               = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_01.fits'  
			template_names[(zsel)&(ebv_0_0)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_01.fits'  
			template_names[(zsel)&(ebv_0_1)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_1.fits'   
			template_names[(zsel)&(ebv_0_2)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_2.fits'   
			template_names[(zsel)&(ebv_0_3)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_3.fits'   
			template_names[(zsel)&(ebv_0_4)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_4.fits'   
			template_names[(zsel)&(ebv_0_5)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_5.fits'   
			template_names[(zsel)&(ebv_1_0)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_1_0.fits'   


	# 'TEMPLATE':str, max 256 char
	t_survey.add_column(Column(name='TEMPLATE', data=template_names, unit=''))
	# 'RULESET':str, max 256 char
	t_survey.add_column(Column(name='RULESET', data=ruleset_array, unit=''))
	# 'REDSHIFT_ESTIMATE':n.float32, 1E
	# 'REDSHIFT_ERROR':n.float32, 1E
	t_survey.add_column(Column(name='REDSHIFT_ESTIMATE', data=t_survey['redshift_R'], unit=''))
	t_survey.add_column(Column(name='REDSHIFT_ERROR', data=n.ones(N_obj), unit=''))
	# 'EXTENT_FLAG': 1I
	# =1
	# 'EXTENT_PARAMETER': 1E
	# =0
	# 'EXTENT_INDEX': 1E
	# =0
	t_survey.add_column(Column(name='EXTENT_FLAG'     , data=n.ones(N_obj).astype('int') , unit=''))
	t_survey.add_column(Column(name='EXTENT_PARAMETER', data=n.zeros(N_obj), unit=''))
	t_survey.add_column(Column(name='EXTENT_INDEX'    , data=n.zeros(N_obj), unit=''))
	# 'MAG':n.float32,
	# 'MAG_ERR':n.float32
	# 'MAG_TYPE': str max 256 char
	r_v=3.1
	a_v = t_survey['galactic_ebv'] * r_v
	delta_mag = n.hstack(( n.array([ extinction.fitzpatrick99(n.array([6500.]), el, r_v=3.1, unit='aa') for el in a_v ]) ))
	#rv = av/ebv
	#av = rv x ebv
	extincted_mag = t_survey['galaxy_mag_r'] + delta_mag
	# fibermag

	def re_dev(M_star): return 0.16 * (M_star)**(0.1) * (1 + M_star / (2.42 * 10**(10)))**(0.76 - 0.1)
	def re_exp(M_star): return 0.08 * (M_star)**(0.16) * (1 + M_star / (17.1 * 10**(10)))**(0.81 - 0.16)
	radius_kpc = re_dev(10**t_survey['galaxy_stellar_mass'])
	radius_arcsec = cosmo.arcsec_per_kpc_proper(t_survey['redshift_R']).value * radius_kpc

	# surface brightness profiles
	# http://ned.ipac.caltech.edu/level5/March05/Graham/Graham2.html
	b4 = 7.669
	b1 = 1.678
	def f_14_dev(r12): return gammainc(8, b4 * (0.7 / r12)**(1. / 6.))
	def f_14_exp(r12): return gammainc(2, b1 * (0.7 / r12)**(1. / 2.)) # From Raichoor 2017
	def f_14_test(r12, nn): return gammainc(2, b1 * (0.7 / r12)**(1. / nn))
	frac = f_14_dev(radius_arcsec)
	flux_fiber = frac * 10**((extincted_mag + 48.6) / -2.5)
	magnitude_4fs2 = -2.5 * n.log10(flux_fiber) - 48.6

	t_survey.add_column(Column(name='MAG', data=magnitude_4fs2, unit='mag'))
	t_survey.add_column(Column(name='MAG_ERR', data=0.01 * n.ones(N_obj), unit='mag'))
	MAG_TYPE = n.ones(N_obj).astype('str')
	MAG_TYPE[:] = 'DECam_r_AB'
	t_survey.add_column(Column(name='MAG_TYPE', data=MAG_TYPE, unit=''))
	# 'REDDENING':n.float32, 1E
	t_survey.add_column(Column(name='REDDENING',data=t_survey['galactic_ebv'], unit='mag'))
	# 'DATE_EARLIEST':n.float64, JulianDate decimal days # 01-Nov-2022
	# 'DATE_LATEST':n.float64, JulianDate decimal days # 02-Feb-2033
	t_survey.add_column(Column(name='DATE_EARLIEST',data=22305 * n.ones(N_obj), unit='d'))
	t_survey.add_column(Column(name='DATE_LATEST'  ,data=33033 * n.ones(N_obj), unit='d'))
	return t_survey



def create_4most_catalogue_sersic(t_survey, subsurvey):
	"""
	Creates a 4MOST subsurvey catalogue for S5
	
	Writes Sersic profile parameters to the Table
	
	t_survey : (astropy Table) simulated catalogue
	subsurvey : (string) sub survey name
	"""
	N_targets=len(t_survey)
	N_obj = len(t_survey)
	#  limit size of the string columns to the size of the longer string in the corresponding columns. 
	# 'NAME':str, max 256 char
	N1 = n.arange(len(t_survey['galactic_ebv']))
	id_list = N_subsurvey[subsurvey]*1e8 + N1
	NAME = n.array([ str(int(el)).zfill(11) for el in id_list ])
	t_survey.add_column(Column(name='NAME', data=NAME, unit=''))
	# 'RA':n.float64, 1D
	# 'DEC':n.float64, 1D
	# 'PMRA':n.float32, 1E
	# 'PMDEC':n.float32, 1E
	# 'EPOCH':n.float32, 1E
	PMRA = n.zeros(N_obj)
	t_survey.add_column(Column(name='RA', data=t_survey['ra'], unit='deg'))
	t_survey.add_column(Column(name='DEC', data=t_survey['dec'], unit='deg'))
	t_survey.add_column(Column(name='PMRA', data=PMRA, unit='mas/yr'))
	PMDEC = n.zeros(N_obj)
	t_survey.add_column(Column(name='PMDEC', data=PMDEC, unit='mas/yr'))
	EPOCH = n.ones(N_obj)*2000.
	t_survey.add_column(Column(name='EPOCH', data=EPOCH, unit='yr'))
	# 'RESOLUTION':n.int16, 1I
	RESOLUTION = n.ones(N_obj).astype('int')
	t_survey.add_column(Column(name='RESOLUTION', data=RESOLUTION, unit=''))
	# 'SUBSURVEY':str, max 256 char
	SUBSURVEY = n.ones(N_obj).astype('str')
	SUBSURVEY[:] = subsurvey
	t_survey.add_column(Column(name='SUBSURVEY', data=SUBSURVEY, unit=''))
	# 'PRIORITY':n.int16, 1I
	PRIORITY = n.zeros(N_obj).astype('int') + priority_values[subsurvey]
	t_survey.add_column(Column(name='PRIORITY', data=PRIORITY, unit=''))

	# EBV for templates
	ebv_1000 = (t_survey['galactic_ebv']*1000).astype('int')
	ebv_1_0 = ( ebv_1000 > 1000 ) 
	ebv_0_5 = ( ebv_1000 > 500 ) & ( ebv_1000 <= 1000 ) 
	ebv_0_4 = ( ebv_1000 > 400 ) & ( ebv_1000 <= 500 ) 
	ebv_0_3 = ( ebv_1000 > 300 ) & ( ebv_1000 <= 400 ) 
	ebv_0_2 = ( ebv_1000 > 200 ) & ( ebv_1000 <= 300 ) 
	ebv_0_1 = ( ebv_1000 > 100 ) & ( ebv_1000 <= 200 ) 
	ebv_0_0 = ( ebv_1000 <= 100 ) 
	z_name = lambda z0, z1 : "_zmin_"+str(int(10*z0)).zfill(2)+"_zmax_"+str(int(10*z1)).zfill(2)
	# templates
	template_names = n.zeros(N_obj).astype('U100')
	ruleset_array = n.zeros(N_obj).astype('str')
	# S8 BG or LRG

	if subsurvey == 'cluster_BCG' :
		ruleset_array[:] = "ClusBCG"
		
	if subsurvey == 'cluster_redGAL':
		ruleset_array[:] = "RedGAL"

	for z0,z1 in zip(zmins,zmaxs):
		zsel = (t_survey['redshift_R']>=z0) & (t_survey['redshift_R']<z1)
		if len(zsel.nonzero()[0])>0:
			#ruleset_array[zsel] = "COSMO_RedGAL"
			template_names[(zsel)]               = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_01.fits'  
			template_names[(zsel)&(ebv_0_0)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_01.fits'  
			template_names[(zsel)&(ebv_0_1)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_1.fits'   
			template_names[(zsel)&(ebv_0_2)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_2.fits'   
			template_names[(zsel)&(ebv_0_3)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_3.fits'   
			template_names[(zsel)&(ebv_0_4)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_4.fits'   
			template_names[(zsel)&(ebv_0_5)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_0_5.fits'   
			template_names[(zsel)&(ebv_1_0)]     = "4most_"+'LRG'+z_name( z0, z1)+'_EBV_1_0.fits'   

	print(n.unique(template_names))
	# 'TEMPLATE':str, max 256 char
	t_survey.add_column(Column(name='TEMPLATE', data=template_names, unit=''))
	# 'RULESET':str, max 256 char
	t_survey.add_column(Column(name='RULESET', data=ruleset_array, unit=''))
	# 'REDSHIFT_ESTIMATE':n.float32, 1E
	# 'REDSHIFT_ERROR':n.float32, 1E
	t_survey.add_column(Column(name='REDSHIFT_ESTIMATE', data=t_survey['redshift_R'], unit=''))
	t_survey.add_column(Column(name='REDSHIFT_ERROR', data=n.ones(N_obj), unit=''))
	
	r_v=3.1
	a_v = t_survey['galactic_ebv'] * r_v
	delta_mag = n.hstack(( n.array([ extinction.fitzpatrick99(n.array([6500.]), el, r_v=3.1, unit='aa') for el in a_v ]) ))
	#rv = av/ebv
	#av = rv x ebv
	extincted_mag = t_survey['galaxy_mag_r'] + delta_mag
	# fibermag

	def re_dev(M_star): return 0.16 * (M_star)**(0.1) * (1 + M_star / (2.42 * 10**(10)))**(0.76 - 0.1)
	def re_exp(M_star): return 0.08 * (M_star)**(0.16) * (1 + M_star / (17.1 * 10**(10)))**(0.81 - 0.16)
	radius_kpc = re_dev(10**t_survey['galaxy_stellar_mass'])
	radius_arcsec = cosmo.arcsec_per_kpc_proper(t_survey['redshift_R']).value * radius_kpc

	# surface brightness profiles
	# http://ned.ipac.caltech.edu/level5/March05/Graham/Graham2.html
	b4 = 7.669
	b1 = 1.678
	def f_14_dev(r12): return gammainc(8, b4 * (0.7 / r12)**(1. / 6.))
	def f_14_exp(r12): return gammainc(2, b1 * (0.7 / r12)**(1. / 2.)) # From Raichoor 2017
	def f_14_test(r12, nn): return gammainc(2, b1 * (0.7 / r12)**(1. / nn))
	frac = f_14_dev(radius_arcsec)
	flux_fiber = frac * 10**((extincted_mag + 48.6) / -2.5)
	magnitude_4fs2 = -2.5 * n.log10(flux_fiber) - 48.6

	# 'EXTENT_FLAG': 1I
	# =1
	# 'EXTENT_PARAMETER': 1E
	# =0
	# 'EXTENT_INDEX': 1E
	# =0
	t_survey.add_column(Column(name='EXTENT_FLAG'     , data=2*n.ones(N_obj).astype('int') , unit=''))
	t_survey.add_column(Column(name='EXTENT_PARAMETER', data=radius_arcsec, unit='arcsec'))
	t_survey.add_column(Column(name='EXTENT_INDEX'    , data=6*n.ones(N_obj), unit=''))
	# 'MAG':n.float32,
	# 'MAG_ERR':n.float32
	# 'MAG_TYPE': str max 256 char

	t_survey.add_column(Column(name='MAG', data=extincted_mag, unit='mag'))
	t_survey.add_column(Column(name='FIBERMAG_johan', data=magnitude_4fs2, unit='mag'))
	t_survey.add_column(Column(name='MAG_ERR', data=0.01 * n.ones(N_obj), unit='mag'))
	MAG_TYPE = n.ones(N_obj).astype('str')
	MAG_TYPE[:] = 'DECam_r_AB'
	t_survey.add_column(Column(name='MAG_TYPE', data=MAG_TYPE, unit=''))
	# 'REDDENING':n.float32, 1E
	t_survey.add_column(Column(name='REDDENING',data=t_survey['galactic_ebv'], unit='mag'))
	# 'DATE_EARLIEST':n.float64, JulianDate decimal days # 01-Nov-2022
	# 'DATE_LATEST':n.float64, JulianDate decimal days # 02-Feb-2033
	t_survey.add_column(Column(name='DATE_EARLIEST',data=22305 * n.ones(N_obj), unit='d'))
	t_survey.add_column(Column(name='DATE_LATEST'  ,data=33033 * n.ones(N_obj), unit='d'))
	return t_survey


#s1 = bcg
#t_survey = Table(hd_clu[s1])
#subsurvey = 'cluster_BCG'
#t_out = create_4most_catalogue_sersic(t_survey, subsurvey)
#t_out.write (path_2_clusterBCG_sersic  , overwrite=True)

s1 = bcg
t_survey = Table(hd_clu[s1])
subsurvey = 'cluster_BCG'
t_out = create_4most_catalogue(t_survey, subsurvey)
t_out.write (path_2_clusterBCG  , overwrite=True)

s1 = cgal
t_survey = Table(hd_clu[s1])
subsurvey = 'cluster_redGAL'
t_out = create_4most_catalogue(t_survey, subsurvey)
t_out.write (path_2_clusterredGAL  , overwrite=True)

