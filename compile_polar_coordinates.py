import os
import shutil
import json
import re
from collections import defaultdict
import numpy as np
import pandas as pd
import cv2
from sc_util import sc_levels, time_stamp
from parse_case_sheet import get_clean_df


def get_ara_level_case_slides():
    with open('case_ara_levels.json', 'r') as f:
        case_ara_levels = json.load(f)
    # re-organize case_ara_levels
    ara_level_case_slides = defaultdict(list)
    for ara_level_case_slide in case_ara_levels.values():
        for ara_level, case_slide in ara_level_case_slide.items():
            ara_level_case_slides[ara_level].append(case_slide)
    return ara_level_case_slides


def get_sc_circle_centers(ara_level):
    # load pre-computed sc circle center
    with open('sc_circle_centers.json', 'r') as f:
        sc_circle_centers = json.load(f)
    return sc_circle_centers[str(ara_level)]


# yields case_id, channel, masked threshold image array at given ara level (int)
def threshold_image_generator(ara_level):
    if ara_level not in sc_levels:
        # StopIteration https://stackoverflow.com/questions/16780002/return-in-generator-together-with-yield-in-python-3-3
        return

    df = get_clean_df()

    # retrieve sc mask
    sc_mask_name = 'sc_masks/sc_mask_{}.tif'.format(str(ara_level).zfill(3))
    sc_mask = cv2.imread(sc_mask_name, 0)

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
            threshold_dir = df_case.loc[pd.IndexSlice[:, channel], 'Case Path (Thresholded Files)'].values[0]
            threshold_name = '{}_ch{}-th.tif'.format(case_slide, channel)
            threshold_path = os.path.join(threshold_dir, threshold_name)
            if not os.path.isfile(threshold_path):
                raise ValueError('{} does not exist'.format(threshold_path))
            threshold = cv2.imread(threshold_path, 0)
            threshold = np.invert(threshold)
            threshold[sc_mask == 0] = 0
            yield case_id, channel, threshold


def compile_polar_coordinates():
    # compute polar coordinates for sections at each sc ara level
    for sc_level in sc_levels:
        print('compiling polar coordinates for ara level {}'.format(sc_level))
        df_polar_coordinates = []
        center_y, center_x = get_sc_circle_centers(sc_level)
        for case_id, channel, threshold in threshold_image_generator(sc_level):
            print(case_id, channel)
            ys, xs = threshold.nonzero()
            # majority of delta_y and delta_x should be positive
            delta_ys = center_y - ys
            delta_xs = xs - center_x
            # theta in radians
            thetas = np.arctan(delta_ys / delta_xs)
            df_polar_coordinates.append(pd.DataFrame({
                'Case ID': case_id,
                'Channel': channel,
                'theta': thetas
            }))
        if len(df_polar_coordinates) == 0:
            continue
        df_polar_coordinates = pd.concat(df_polar_coordinates)
        df_polar_coordinates.to_csv('polar_coordinates/polar_coordinates_ara_{}.csv'.format(str(sc_level).zfill(3)))


if __name__ == '__main__':
    os.makedirs('polar_coordinates', exist_ok=True)
    compile_polar_coordinates()
