import os
import json
import time
import re
from collections import defaultdict
import numpy as np
import pandas as pd
import cv2
from parse_case_sheet import get_clean_df


sc_levels = range(83, 105)

sc_custom_atlas_levels = [86, 90, 96, 100]

sc_custom_centers = {
    '86': [5812, 7355.5],
    '90': [5504, 7355.5],
    '96': [5431, 7355.5],
    '100': [4964, 7355.5]
}

sc_codecs = {
    '254:121:255': 'Scig_b', '254:132:253': 'SCs_zo', '254:132:254': 'SCs_sg', '254:132:255': 'SCs_op',
    '254:133:249': 'SCm_dw', '254:133:250': 'SCm_ig', '254:133:251': 'SCM_ig-c', '254:133:252': 'SCM_ig-b',
    '254:133:253': 'SCM_ig-a', '254:133:254': 'SCm_iw', '254:133:255': 'SCm_dg'
}

atlas_dimension = (11012, 14712)

version = 'v1.1'


def time_stamp(output_format='Y-%m-%d-%H:%M:%S'):
    return time.strftime(output_format, time.localtime())


def plots_out_dir():
    d = os.path.join('plots', version)
    os.makedirs(d, exist_ok=True)
    return d


def get_sc_circle_centers(ara_level, use_custom_centers=False):
    ara_level = str(ara_level)
    # load pre-computed sc circle center
    with open('sc_circle_centers.json', 'r') as f:
        sc_circle_centers = json.load(f)
    if use_custom_centers:
        if ara_level in sc_custom_centers:
            return sc_custom_centers[ara_level]
    return sc_circle_centers[ara_level]


def get_case_ara_levels():
    with open('case_ara_levels.json', 'r') as f:
        case_ara_levels = json.load(f)
    return case_ara_levels


def get_ara_level_case_slides():
    case_ara_levels = get_case_ara_levels()
    # re-organize case_ara_levels
    ara_level_case_slides = defaultdict(list)
    for ara_level_case_slide in case_ara_levels.values():
        for ara_level, case_slide in ara_level_case_slide.items():
            ara_level_case_slides[ara_level].append(case_slide)
    return ara_level_case_slides


# yields case_id, (case_slide), channel, (masked) threshold image array
# at given ara level (int). threshold image is returned with signal set to 255
def threshold_image_generator(ara_level, apply_sc_mask=True, return_case_slide=False):
    ara_level = int(ara_level)
    if ara_level not in sc_levels:
        # StopIteration https://stackoverflow.com/questions/16780002/return-in-generator-together-with-yield-in-python-3-3
        return

    df = get_clean_df()

    # retrieve sc mask
    if apply_sc_mask:
        sc_mask_name = 'sc_masks/sc_mask_{}.tif'.format(str(ara_level).zfill(3))
        sc_mask = cv2.imread(sc_mask_name, 0)
    else:
        sc_mask = np.ones(shape=atlas_dimension, dtype=np.uint8)

    ara_level_case_slides = get_ara_level_case_slides()
    # retrieve case_slide ids for the ara level
    case_slides = ara_level_case_slides[str(ara_level)]

    # retrieve items to be yielded
    for case_slide in case_slides:
        # case pattern without series identifier, to acommadate df index level 'Case ID' entries such as SW110613-03B/A
        case_pattern = '[A-Z]{2}[0-9]{6}-[0-9]{2}'
        # find matching case id (ignoring series identifier) in df
        case = re.match(case_pattern, case_slide).group()
        df_case = df.loc[df.index.get_level_values('Case ID').str.match(case), :]
        # case id with series identifier
        case_id = pd.unique(df_case.index.get_level_values('Case ID'))[0]
        # for each channel of the case, load threshold image
        channels = df_case.index.get_level_values('Channel')
        for channel in channels:
            # use image in post-erase folder if exists
            threshold_channel_dir = df_case.loc[pd.IndexSlice[:, channel], 'Case Path (Thresholded Files)'].values[0]
            tokens = threshold_channel_dir.split('/')
            tokens[-2] = 'post-erase'
            threshold_post_erase_dir = '/'.join(tokens)
            threshold_name = '{}_ch{}-th.tif'.format(case_slide, channel)
            threshold_channel_path = os.path.join(threshold_channel_dir, threshold_name)
            threshold_post_erase_path = os.path.join(threshold_post_erase_dir, threshold_name)
            if os.path.isfile(threshold_post_erase_path):
                threshold_path = threshold_post_erase_path
            else:
                threshold_path = threshold_channel_path
            print(threshold_path)
            if not os.path.isfile(threshold_path):
                raise ValueError('{} does not exist'.format(threshold_path))
            threshold = cv2.imread(threshold_path, 0)
            threshold = np.invert(threshold)
            if apply_sc_mask:
                threshold[sc_mask == 0] = 0
            # case_id can be in the form SW121031-03B/A
            if not return_case_slide:
                yield case_id, channel, threshold
            else:
                yield case_id, case_slide, channel, threshold
