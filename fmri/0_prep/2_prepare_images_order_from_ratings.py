'''

Prepare stimuli order for the scanning sessions

This script creates the stimuli order for a specific subject and session as indicated by the users.
It needs the input files from the image selection process (matter.txt, stock.txt, neutral.txt, selected_matter_ratings_info.xlsx,
matter_EMOinfo.txt)

Outputs should be copied to the Stimulus PC to run the experiment.

'''



import os, glob
import numpy as np
import pandas as pd
import shutil
import random
from utils.randomise import generate_random_sequence_2cond_maxCons, shuffle_without_consecutive_duplicates

####################################################################
#   User should change this before running the script!!!           #
####################################################################

SESSION_NR = 1
NR_LOC_RUNS = 0
NR_NF_RUNS = 0
NR_TRANS_RUNS = 0
NR_RECALL_RUNS = 1
NR_BLOCKS = 16

####################################################################


sub_name = input('Insert the subject name: ')
group = input('Insert group (matter or stock): ')

wdir = f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data_local/behavioural/initial_ratings/{sub_name}'
outdir = f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/stim_prep/{sub_name}'

# make directory for the current subject in data
os.makedirs(outdir, exist_ok=True)

# get images list and prepare order files for localiser and NF runs

if group == 'stock':

    # create the session folder
    ses_folder = f'{outdir}/ses-0{SESSION_NR}'
    os.makedirs(ses_folder, exist_ok=True)

    # get the ratings of for the stock images
    stock_images_file = glob.glob(f'{wdir}/stock.txt')[0]
    images_list = []

    with open(stock_images_file, 'r') as file:
        for line in file:
            images_list.append(line)

    # prepare images order for the NF runs
    for run in range(NR_NF_RUNS):

        # create the run folder
        run_folder = f'{outdir}/ses-0{SESSION_NR}/runNF{run + 1}'
        os.makedirs(run_folder, exist_ok=True)

        # for stock pictures we can simply randomise and duplicate the frequency of each image
        images_NF_temp = images_list.copy()
        random.shuffle(images_NF_temp)

        # choose which image should be scrambled (4 per run)
        scramble_idx = np.arange(len(images_NF_temp))
        random.shuffle(scramble_idx)
        scramble_idx = scramble_idx[:4]

        images_NF = []
        for item_idx, item in enumerate(images_NF_temp):
            if item_idx not in scramble_idx:
                images_NF.extend([item] * 2)
            else:
                scramble_img_pos = np.array([0,1]) # decide if the scramble image is the first or the second presented
                random.shuffle(scramble_img_pos)
                scramble_img_pos = scramble_img_pos[0]

                if scramble_img_pos == 0:
                    images_NF.extend(['_scrambled_db/'+item, item])
                else:
                    images_NF.extend([item, '_scrambled_db/' + item])

        # save the run order file
        # the NF script looks for runNFX_group.txt
        order_filename = f'{run_folder}/runNF{run+1}_{group}.txt'

        with open(order_filename,'w') as f:
            for image in images_NF:
                f.write(f'{image}')

    # copy also the folder of the neutral images and add the names to the image list to create the order file for the localiser
    # get the ratings of for the stock images
    neutral_images = []

    with open(f'{wdir}/neutral.txt', 'r') as file:
        for line in file:
            neutral_images.append(line)

    for run in range(NR_LOC_RUNS):
        # create localiser images folder balancing the frequency that one condition follows the other
        # get balanced sequence
        seq = generate_random_sequence_2cond_maxCons('positive', 'neutral', NR_BLOCKS, balance_factor=0.5, max_consecutive = 2)
        print('Localiser condition sequence:')
        print(seq)

        idx_pos = 0
        idx_neu = 0

        images_localiser = []

        # shuffle neutral and positive images
        random.shuffle(images_list)
        random.shuffle(neutral_images)

        for cond in seq:
            if cond == 'positive' and idx_pos < NR_BLOCKS/2:
                images_localiser.append(images_list[idx_pos])
                idx_pos += 1

            elif cond == 'neutral' and idx_neu < NR_BLOCKS/2:
                images_localiser.append(f'{neutral_images[idx_neu]}')
                idx_neu += 1

        # save the run order file for the Localiser
        # the Localiser script looks for Localiser_group.txt
        order_filename = f'{ses_folder}/Localiser{run+1}_{group}.txt'

        with open(order_filename, 'w') as f:
            for image in images_localiser:
                f.write(f'{image}')


    for run in range(NR_TRANS_RUNS):

        # for stock pictures we can simply randomise and duplicate the frequency of each image
        images_temp = images_list.copy()
        random.shuffle(images_temp)

        # choose which image should be scrambled (4 per run)
        scramble_idx = np.arange(len(images_temp))
        random.shuffle(scramble_idx)
        scramble_idx = scramble_idx[:4]

        images_NF = []
        for item_idx, item in enumerate(images_temp):
            if item_idx not in scramble_idx:
                images_NF.extend([item] * 2)
            else:
                scramble_img_pos = np.array([0, 1])  # decide if the scramble image is the first or the second presented
                random.shuffle(scramble_img_pos)
                scramble_img_pos = scramble_img_pos[0]

                if scramble_img_pos == 0:
                    images_NF.extend(['_scrambled_db/' + item, item])
                else:
                    images_NF.extend([item, '_scrambled_db/' + item])

        # save the run order file
        # the NF script looks for runNFX_group.txt
        order_filename = f'{ses_folder}/Transfer{run + 1}_{group}.txt'

        with open(order_filename, 'w') as f:
            for image in images_NF:
                f.write(f'{image}')


elif group == 'matter':

    # create the session folder
    ses_folder = f'{outdir}/ses-0{SESSION_NR}'
    os.makedirs(ses_folder, exist_ok=True)

    # get the ratings of for the stock images
    matter_images_file = glob.glob(f'{wdir}/matter.txt')[0]
    images_emo_info = pd.read_excel(f'{wdir}/selected_matter_ratings_info.xlsx')

    images_list = []
    emo_order = []

    with open(matter_images_file, 'r') as file:
        for line in file:
            images_list.append(line[:-1]+'.jpg\n')
            cur_emo = images_emo_info['Peak Labels'][images_emo_info['Image ID'] == line[:-1]].values[0]
            emo_order.append(f'{cur_emo}_{images_list[-1]}')


    # prepare images order for the NF runs
    for run in range(NR_NF_RUNS): # check this later for others

        # create the run folder
        run_folder = f'{outdir}/ses-0{SESSION_NR}/runNF{run + 1}'
        os.makedirs(run_folder, exist_ok=True)

        # for stock pictures we can simply randomise and duplicate the frequency of each image
        images_NF_temp = emo_order.copy() #images + emotion label
        images_NF_temp, indices = shuffle_without_consecutive_duplicates(images_NF_temp)

        #remove emotion label
        images_NF_temp = [item.split('_')[1] for item in images_NF_temp]

        # choose which image should be scrambled (4 per run), balance condition
        # scramble_idx = np.arange(len(images_temp))
        # random.shuffle(scramble_idx)
        # scramble_idx = scramble_idx[:4]
        scramble_idx = np.array([0, 2, 4, 6])
        rand_ = np.array([random.randint(0, 1) for _ in range(4)])
        scramble_idx = rand_ + scramble_idx

        images_NF = []
        for item_idx, item in enumerate(images_NF_temp):
            if indices[item_idx] not in scramble_idx:
                images_NF.extend([item] * 2)
            else:
                scramble_img_pos = np.array([0, 1])  # decide if the scramble image is the first or the second presented
                random.shuffle(scramble_img_pos)
                scramble_img_pos = scramble_img_pos[0]

                if scramble_img_pos == 0:
                    images_NF.extend(['_scrambled_db/' + item, item])
                else:
                    images_NF.extend([item, '_scrambled_db/' + item])

        # save the run order file
        # the NF script looks for runNFX_group.txt
        order_filename = f'{run_folder}/runNF{run + 1}_{group}.txt'

        with open(order_filename, 'w') as f:
            for image in images_NF:
                f.write(f'{image}')

    # copy also the folder of the neutral images and add the names to the image list to create the order file for the localiser
    # get the ratings of for the stock images
    neutral_images = []

    with open(f'{wdir}/neutral.txt', 'r') as file:
        for line in file:
            neutral_images.append(line)

    for run in range(NR_LOC_RUNS):
        # create localiser images folder balancing the frequency that one condition follows the other
        # get balanced sequence
        seq = generate_random_sequence_2cond_maxCons('positive', 'neutral', NR_BLOCKS, balance_factor=0.5,
                                                     max_consecutive=2)
        print('Localiser condition sequence:')
        print(seq)

        idx_pos = 0
        idx_neu = 0

        images_localiser = []

        # shuffle neutral and positive images
        random.shuffle(images_list)
        random.shuffle(neutral_images)

        for cond in seq:
            if cond == 'positive' and idx_pos < NR_BLOCKS / 2:
                images_localiser.append(images_list[idx_pos])
                idx_pos += 1

            elif cond == 'neutral' and idx_neu < NR_BLOCKS / 2:
                images_localiser.append(f'{neutral_images[idx_neu]}')
                idx_neu += 1

        # save the run order file for the Localiser
        # the Localiser script looks for Localiser_group.txt
        order_filename = f'{ses_folder}/Localiser{run + 1}_{group}.txt'

        with open(order_filename, 'w') as f:
            for image in images_localiser:
                f.write(f'{image}')

    for run in range(NR_RECALL_RUNS):

        # get the ratings of for the stock images
        matter_images_file = glob.glob(f'{wdir}/matter_EMOinfo.txt')[0]
        images_list_recall = []

        with open(matter_images_file, 'r') as file:
            for line in file:
                images_list_recall.append(line[:-1]+'.jpg\n')

        # for stock pictures we can simply randomise and duplicate the frequency of each image
        images_temp = images_list_recall.copy()
        images_temp, indices = shuffle_without_consecutive_duplicates(images_temp)

        images_temp = [item.split('_')[1] for item in images_temp]

        # choose which image should be scrambled (4 per run), balance condition
        #scramble_idx = np.arange(len(images_temp))
        # random.shuffle(scramble_idx)
        # scramble_idx = scramble_idx[:4]
        scramble_idx = np.array([0,2,4,6])
        rand_ = np.array([random.randint(0, 1) for _ in range(4)])
        scramble_idx = rand_ + scramble_idx

        images_NF = []
        for item_idx, item in enumerate(images_temp):
            if indices[item_idx] not in scramble_idx:
                images_NF.extend([item] * 2)
            else:
                scramble_img_pos = np.array([0, 1])  # decide if the scramble image is the first or the second presented
                random.shuffle(scramble_img_pos)
                scramble_img_pos = scramble_img_pos[0]

                if scramble_img_pos == 0:
                    images_NF.extend(['_scrambled_db/' + item, item])
                else:
                    images_NF.extend([item, '_scrambled_db/' + item])

        # save the run order file
        # the NF script looks for runNFX_group.txt
        order_filename = f'{ses_folder}/Recall{run + 1}_{group}.txt'

        with open(order_filename, 'w') as f:
            for image in images_NF:
                f.write(f'{image}')

    for run in range(NR_TRANS_RUNS):

        # get the ratings of for the stock images
        matter_images_file = glob.glob(f'{wdir}/matter_EMOinfo.txt')[0]
        images_list_recall = []

        with open(matter_images_file, 'r') as file:
            for line in file:
                images_list_recall.append(line[:-1] + '.jpg\n')

        # for stock pictures we can simply randomise and duplicate the frequency of each image
        images_temp = images_list_recall.copy()
        images_temp, indices = shuffle_without_consecutive_duplicates(images_temp)

        images_temp = [item.split('_')[1] for item in images_temp]

        # choose which image should be scrambled (4 per run), balance condition
        # scramble_idx = np.arange(len(images_temp))
        # random.shuffle(scramble_idx)
        # scramble_idx = scramble_idx[:4]
        scramble_idx = np.array([0, 2, 4, 6])
        rand_ = np.array([random.randint(0, 1) for _ in range(4)])
        scramble_idx = rand_ + scramble_idx

        images_NF = []
        for item_idx, item in enumerate(images_temp):
            if indices[item_idx] not in scramble_idx:
                images_NF.extend([item] * 2)
            else:
                scramble_img_pos = np.array(
                    [0, 1])  # decide if the scramble image is the first or the second presented
                random.shuffle(scramble_img_pos)
                scramble_img_pos = scramble_img_pos[0]

                if scramble_img_pos == 0:
                    images_NF.extend(['_scrambled_db/' + item, item])
                else:
                    images_NF.extend([item, '_scrambled_db/' + item])

        # save the run order file
        # the NF script looks for runNFX_group.txt
        order_filename = f'{ses_folder}/Transfer{run + 1}_{group}.txt'

        with open(order_filename, 'w') as f:
            for image in images_NF:
                f.write(f'{image}')






































# create file with the images order for the localiser
