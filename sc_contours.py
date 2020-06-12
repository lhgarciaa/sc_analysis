import os
import numpy as np
import cv2


os.makedirs('sc_contours', exist_ok=True)
for mask_name in os.listdir('sc_masks'):
    mask = cv2.imread(os.path.join('sc_masks/{}'.format(mask_name)), 0)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    output = np.zeros(shape=mask.shape, dtype=np.uint8)
    output = cv2.drawContours(output, contours, -1, 255)
    cv2.imwrite('sc_contours/{}'.format(mask_name.replace('mask', 'contour')), output)
