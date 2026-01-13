'''

fMRI Data Offline Pre-processing (BV)

This script should run within BV python console.

It creates an FMR file from dicom files and performs standard preprocessing steps including:

- Slice scan time correction
- Motion correction
- High-pass filtering
- 3D Gaussian smoothing

It is meant to be used with 2 Localiser runs from the first session to prepare the target region for the NF sessions

'''


import glob, os
import math
import shutil
from bvbabel import fmr

################################################################################
#                                USER INPUTS                                   #
################################################################################

wdir = 'D:/MatterNeurofeedback/raw_data/StandardNF'
outdir = 'D:/MatterNeurofeedback/derivatives/rawdata_bv'

# Indicate subject ID and the series number for
sub = 'sub-16'
loc_ser_nr1 = '13'
loc_ser_nr2 = '17'

# Functional images info
loc_ser_num = [loc_ser_nr1, loc_ser_nr2]
NR_SLICES = 72
IN_PLANE_RESOLUTION = (110, 110)
mosaic_row =990
mosaic_col =990
VOL_NUM = 660 # length of the time series

# High Pass Filter Cut-off
HPF_CUTOFF = 0.009

# create temporary directory for the dicom files (since BV changes )
if os.path.exists(f'{wdir}/temp'):
    shutil.rmtree(f'{wdir}/temp')

os.makedirs(f'{wdir}/temp', exist_ok=True)

# creating output directory for this subject
subdir = f'{outdir}/{sub}/'
os.makedirs(subdir, exist_ok=True)

os.makedirs(f'{subdir}/ses-01/', exist_ok=True)

procdir = f'{subdir}/ses-01/func/'
os.makedirs(procdir, exist_ok=True)

fmr_names = [f'{sub}_ses-01_dir-AP_task-localiser2_run-02', f'{sub}_ses-01_dir-AP_task-localiser3_run-03']

################################################################################
#                              START PREPROCESSING                             #
################################################################################


for i, cur_ser_nr in enumerate([loc_ser_nr1, loc_ser_nr2]):

    dcm_format = f'00*_{cur_ser_nr.zfill(6)}_000*'

    dicom_files = glob.glob(f'{wdir}/{sub}/ses-01/tbv/{dcm_format}')
    print(f'\nWorking on series number {cur_ser_nr}')
    print(f'\nFound {len(dicom_files)} files.')

    # copy the dicom files for the current run to a temporary folder to avoid renaming the original files
    for dcm in dicom_files:
        shutil.copy(dcm,f'{wdir}/temp/{os.path.basename(dcm)}')

    first_dcm = f'{wdir}/temp/001_{cur_ser_nr.zfill(6)}_000001.dcm'
    print('\nFirst dicom: ' + first_dcm)

    doc = bv.create_mosaic_fmr(first_dcm.replace("\\", "/"), VOL_NUM, 0, False, NR_SLICES, fmr_names[i], False,
                                        mosaic_row, mosaic_col, IN_PLANE_RESOLUTION[0], IN_PLANE_RESOLUTION[1], 2,
                                         procdir)
    doc.save_as(f'{procdir}/{fmr_names[i]}')

    doc.close()

    print('\nFile Saved.')
    path_run = f'{procdir}/{fmr_names[i]}.fmr'

    # 1// Correct Slice Timing
    print('\nStart correcting slice time for {}'.format(path_run))
    docFMR = bv.open(path_run)
    docFMR.correct_slicetiming_using_timingtable(1)  # cubic spline (recommended), check subject sub-08
    Fnme_newFMR = docFMR.preprocessed_fmr_name
    docFMR.close()
    print('\nDone with correcting slice timing'.format(path_run))

    if i == 0:
        MOCO_REF_VOL = Fnme_newFMR

    print('\nStart correcting motion for {}'.format(path_run))

    # 2// Motion Correction
    docFMR = bv.open(Fnme_newFMR)
    docFMR.correct_motion_to_run_ext(MOCO_REF_VOL, 0, 2, 1, 100, 1, 1)
    Fnme_newFMR = docFMR.preprocessed_fmr_name
    docFMR.close()
    print('\nDone with correcting motion'.format(path_run))

    # 3// High Pass Filtering
    print('\nStart HPF for {}'.format(path_run))
    docFMR=bv.open(Fnme_newFMR)
    docFMR.filter_temporal_highpass_fft(HPF_CUTOFF,'Hz')
    Fnme_newFMR = docFMR.preprocessed_fmr_name
    docFMR.close()

    #change naming
    hdr, data = fmr.read_fmr(Fnme_newFMR)
    new_filename = Fnme_newFMR[:-13] + 'LTR_THPFFT0.0090Hz.fmr'
    fmr.write_fmr(new_filename, hdr, data)

    # delete old files
    os.remove(Fnme_newFMR)
    os.remove(Fnme_newFMR[:-4]+'.stc')

    # 4// Smoothing
    docFMR = bv.open(new_filename)
    docFMR.smooth_spatial(3.6, 'mm')
    docFMR.close()