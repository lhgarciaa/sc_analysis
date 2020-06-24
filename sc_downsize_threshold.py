import os
import re
import numpy as np
import cv2
from parse_case_sheet import get_clean_df
from sc_util import sc_levels, sc_custom_atlas_levels, sc_custom_centers, threshold_image_generator


def get_custom_wireframe(ara_level, use_custom_centers=False):
    if use_custom_centers and str(ara_level) in sc_custom_centers:
        root = 'sc_custom_center_outputs/'
    else:
        root = ''
    if ara_level in sc_custom_atlas_levels:
        wireframe_path = root + 'sc_wires/SC/v3/{}_SC_rgb_atlas_wire_with_angle_lines.tif'.format(str(ara_level).zfill(3))
    else:
        wireframe_path = root + 'sc_wires/ARA/ARA-Coronal-{}_full_labels-01-append_wire_with_angle_lines.tif'.format(str(ara_level).zfill(3))
    return cv2.imread(wireframe_path, cv2.IMREAD_GRAYSCALE)


def make_downsize_threshold(sc_level, use_custom_centers=False):
    df = get_clean_df()
    wireframe = get_custom_wireframe(sc_level, use_custom_centers=use_custom_centers)
    tracer_rgb_map = {
        'aav-tdtomato': (228, 26, 28),
        'aav-gfp': (228, 26, 28),
        'phal-647': (152, 78, 163),
        'phal-488': (77, 175, 74),
        'bda': (228, 26, 28),
        'phal': (77, 175, 74)
    }
    for case_id, case_slide, channel, threshold in threshold_image_generator(sc_level, apply_sc_mask=False, return_case_slide=True):
        tracer = df.loc[(case_id, channel), 'Tracers']
        # handle case id in the form of SW121031-03B/A
        case_id = re.match('[A-Z]{2}[0-9]{6}-[0-9]{2}[A-D]{1}', case_id).group()
        if not use_custom_centers:
            output_root_dir = 'sc_threshold_downsize'
        else:
            output_root_dir = 'sc_custom_center_outputs/sc_threshold_downsize'
        output_dir = os.path.join(output_root_dir, case_id, 'threshold', 'channels', channel)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        threshold_r = np.ones(shape=threshold.shape, dtype=np.uint8) * 255
        threshold_r[threshold > 0] = tracer_rgb_map[tracer][0]
        threshold_r[wireframe < 255] = 0
        threshold_g = np.ones(shape=threshold.shape, dtype=np.uint8) * 255
        threshold_g[threshold > 0] = tracer_rgb_map[tracer][1]
        threshold_g[wireframe < 255] = 0
        threshold_b = np.ones(shape=threshold.shape, dtype=np.uint8) * 255
        threshold_b[threshold > 0] = tracer_rgb_map[tracer][2]
        threshold_b[wireframe < 255] = 0
        threshold_bgr = cv2.merge([threshold_b, threshold_g, threshold_r])
        for i in range(3):
            threshold_bgr = cv2.pyrDown(threshold_bgr)
        cv2.imwrite(os.path.join(output_dir, '{}_ch{}-th.tif'.format(case_slide, channel)), threshold_bgr)


def main():
    for sc_level in sc_levels:
        make_downsize_threshold(sc_level)

if __name__ == '__main__':
    main()
