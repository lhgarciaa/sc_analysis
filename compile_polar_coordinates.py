import os
import numpy as np
import pandas as pd
from sc_util import sc_levels, get_sc_circle_centers, threshold_image_generator


def compile_polar_coordinates():
    # compute polar coordinates for sections at each sc ara level
    for sc_level in sc_levels:
        print('compiling polar coordinates for ara level {}'.format(sc_level))
        df_polar_coordinates = []
        center_y, center_x = get_sc_circle_centers(sc_level)
        for case_id, channel, threshold in threshold_image_generator(sc_level, apply_sc_mask=True, return_case_slide=False):
            print(case_id, channel)
            ys, xs = threshold.nonzero()
            # majority of delta_y and delta_x should be positive
            delta_ys = center_y - ys
            delta_xs = xs - center_x
            # theta in radians
            thetas = np.arctan(delta_ys / delta_xs)
            df_polar_coordinates.append(pd.DataFrame({
                'case': case_id,
                'channel': channel,
                'theta': thetas
            }))
        if len(df_polar_coordinates) == 0:
            continue
        df_polar_coordinates = pd.concat(df_polar_coordinates)
        df_polar_coordinates.to_csv('polar_coordinates/polar_coordinates_ara_{}.csv'.format(str(sc_level).zfill(3)))


if __name__ == '__main__':
    os.makedirs('polar_coordinates', exist_ok=True)
    compile_polar_coordinates()
