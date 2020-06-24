# compile polar coordinates for levels with custom center
# downsized threshold with custom center
import os
import cv2
from sc_util import sc_custom_centers, plots_out_dir
from sc_angle_lines import draw_angle_lines
from compile_polar_coordinates import compile_polar_coordinates
from sc_downsize_threshold import make_downsize_threshold
from regroup_downsized_threshold import regroup_downsized_threshold


def compile_polar_coordinates_with_custom_centers():
    os.makedirs('sc_custom_center_outputs/polar_coordinates', exist_ok=True)
    for sc_level in sc_custom_centers:
        df = compile_polar_coordinates(sc_level, use_custom_centers=True)
        df.to_csv('sc_custom_center_outputs/polar_coordinates/polar_coordinates_ara_{}.csv'.format(sc_level.zfill(3)))


def draw_angle_lines_with_custom_centers():
    os.makedirs('sc_custom_center_outputs/sc_angle_lines', exist_ok=True)
    for sc_level in sc_custom_centers:
        angle_lines = draw_angle_lines(sc_level, use_custom_centers=True)
        cv2.imwrite('sc_custom_center_outputs/sc_angle_lines/sc_angle_lines_ara_{}.tif'.format(sc_level.zfill(3)), angle_lines)


def make_atlas_wireframe_and_angle_lines_with_custom_centers():
    angle_line_dir = 'sc_custom_center_outputs/sc_angle_lines'
    wire_input_formats = {
        'sc_wires/ARA': 'ARA-Coronal-{}_full_labels-01-append_wire.tif',
        'sc_wires/SC/v1': '{}_sc_wire.tif',
        'sc_wires/SC/v3': '{}_SC_rgb_atlas_wire.tif'
    }
    wire_output_formats = {
        'sc_wires/ARA': 'ARA-Coronal-{}_full_labels-01-append_wire_with_angle_lines.tif',
        'sc_wires/SC/v1': '{}_sc_wire_with_angle_lines.tif',
        'sc_wires/SC/v3': '{}_SC_rgb_atlas_wire_with_angle_lines.tif'
    }
    output_root_dir = 'sc_custom_center_outputs'
    for wire_input_dir, wire_input_format in wire_input_formats.items():
        output_dir = os.path.join(output_root_dir, wire_input_dir)
        os.makedirs(output_dir, exist_ok=True)
        for sc_level in sc_custom_centers:
            atlas_wire_path = os.path.join(wire_input_dir, wire_input_format.format(sc_level.zfill(3)))
            if not os.path.isfile(atlas_wire_path):
                continue
            atlas_wire = cv2.imread(os.path.join(wire_input_dir, wire_input_format.format(sc_level.zfill(3))), 0)
            angle_lines = cv2.imread(os.path.join(angle_line_dir, 'sc_angle_lines_ara_{}.tif'.format(sc_level.zfill(3))), 0)
            atlas_wire[angle_lines < 255] = 0
            cv2.imwrite(os.path.join(output_dir, wire_output_formats[wire_input_dir].format(sc_level.zfill(3))), atlas_wire)


def make_downsize_threshold_with_custom_centers():
    for sc_level in sc_custom_centers:
        make_downsize_threshold(sc_level, use_custom_centers=True)


def regroup_downsized_threshold_with_custom_centers():
    regroup_downsized_threshold(use_custom_centers=True)



def main():
    os.makedirs('sc_custom_center_outputs', exist_ok=True)
    #compile_polar_coordinates_with_custom_centers()
    #draw_angle_lines_with_custom_centers()
    #make_atlas_wireframe_and_angle_lines_with_custom_centers()
    #make_downsize_threshold_with_custom_centers()
    regroup_downsized_threshold_with_custom_centers()


main()
