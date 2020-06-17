import os
import json
import math
import numpy as np
import cv2
from sc_util import atlas_dimension, sc_levels, get_sc_circle_centers


# theta is in radians
def draw_angle_line(image, theta, y_start, x_start):
    assert 0 <= theta <= np.pi / 2
    # plot 10 pixels, skip 3 pixels
    segment_length = 20
    segment_skip = 10
    y_start, x_start = int(y_start), int(x_start)
    x_max = atlas_dimension[1]

    while y_start >= 0 and x_start < x_max:
        # draw solid segment of length 10
        y_end = max(0, int(round(y_start - math.sin(theta) * segment_length)))
        x_end = min(x_max, int(round(x_start + math.cos(theta) * segment_length)))
        image = cv2.line(image, (x_start, y_start), (x_end, y_end), 0, thickness=5, lineType=cv2.LINE_4)
        y_start = int(round(y_end - math.sin(theta) * segment_skip))
        x_start = int(round(x_end + math.cos(theta) * segment_skip))
    return image


def draw_angle_lines(ara_level):
    ara_level = str(ara_level)
    y_center, x_center = get_sc_circle_centers(ara_level)
    output = np.invert(np.zeros(shape=atlas_dimension, dtype=np.uint8))
    for theta in range(0, 100, 10):
        output = draw_angle_line(output, theta * np.pi / 180, y_center, x_center)
    return output


def draw_sc_angle_lines():
    os.makedirs('sc_angle_lines', exist_ok=True)
    for sc_level in sc_levels:
        angle_lines = draw_angle_lines(sc_level)
        cv2.imwrite('sc_angle_lines_ara_{}.tif'.format(str(sc_level).zfill(3)), angle_lines)


if __name__ == '__main__':
    draw_sc_angle_lines()
