import os
import re
import numpy as np
import cv2


def make_atlas_wire(atlas_path):
    assert os.path.isfile(atlas_path)
    atlas = cv2.imread(atlas_path, -1)
    atlas_canny = cv2.Canny(atlas, 0, 1)
    kernel = np.ones((5, 5), np.uint8)
    wire = cv2.dilate(atlas_canny, kernel, iterations=2)
    wire = np.invert(wire)
    wire_bgr = cv2.merge([wire, wire, wire])
    return wire_bgr


def make_atlas_wires(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for image_name in os.listdir(input_dir):
        if not image_name.endswith('.tif'):
            continue
        atlas_wire = make_atlas_wire(os.path.join(input_dir, image_name))
        cv2.imwrite(os.path.join(output_dir, image_name.replace('.tif', '_wire.tif')), atlas_wire)
        ara_level = re.search('[0-9]{3}', image_name).group()
        angle_lines = cv2.imread('sc_angle_lines/sc_angle_lines_ara_{}.tif'.format(ara_level))
        atlas_wire[angle_lines < 255] = 0
        cv2.imwrite(os.path.join(output_dir, image_name.replace('.tif', '_wire_with_angle_lines.tif')), atlas_wire)


if __name__ == '__main__':
    make_atlas_wires('sc_atlas/ARA', 'sc_wires/ARA')
    make_atlas_wires('sc_atlas/SC/v1', 'sc_wires/SC/v1')
    make_atlas_wires('sc_atlas/SC/v3', 'sc_wires/SC/v3')
