import json
import numpy as np
import cv2
from sc_util import sc_levels


sc_circle_centers = {}
for sc_level in sc_levels:
    # fit line to lateral radial boundary of SC
    contour = cv2.imread('sc_contours_partial/sc_contour_partial_{}.tif'.format(str(sc_level).zfill(3)), 0)
    pts = np.array(np.where(contour > 0))
    pts[[0, 1]] = pts[[1, 0]]
    # all numbers returned as shape (1,) array
    vx, vy, x0, y0 = cv2.fitLine(np.transpose(pts), cv2.DIST_L2, 0, 0.01, 0.01)
    # calculate circle center coordinate as intersection between fitted line and midline
    slope = vy / vx
    intercept = y0 - slope * x0
    x_center = 14711 / 2
    y_center = (slope * x_center + intercept)[0]
    print(sc_level, y_center, x_center)
    sc_circle_centers[sc_level] = [float(y_center), float(x_center)]

with open('sc_circle_centers.json', 'w') as f:
    json.dump(sc_circle_centers, f)
