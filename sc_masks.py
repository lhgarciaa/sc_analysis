import os
import numpy as np
import cv2
from translate_colors import TranslateColors
from sc_util import sc_levels, sc_codecs


codec = TranslateColors()
sc_indices = [TranslateColors.colorstring_to_index(sc_codec) for sc_codec in sc_codecs]

os.makedirs('sc_masks', exist_ok=True)
for sc_level in sc_levels:
    atlas_tiff_name = 'ARA-Coronal-{}_full_labels-01-append.tif'.format(str(sc_level).zfill(3))
    atlas = cv2.imread('sc_atlas/{}'.format(atlas_tiff_name), -1)
    atlas = TranslateColors.rgbatlas_to_indexatlas(atlas)
    mask = np.zeros(shape=atlas.shape, dtype=np.uint8)
    # only right sc regions are white
    mask[np.isin(atlas, sc_indices)] = 255
    mask[:, 0: mask.shape[1] // 2] = 0
    cv2.imwrite('sc_masks/sc_mask_{}.tif'.format(str(sc_level).zfill(3)), mask)
