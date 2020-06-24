import os
import shutil
import re
import pandas as pd
from parse_case_sheet import get_clean_df
from sc_util import get_case_ara_levels, sc_levels, sc_custom_centers


# second group is ara_level
def regroup_downsized_threshold(first_group='Actual Anatomical/ Injection Site Primary', use_custom_centers=False):
    if use_custom_centers:
        output_root_dir = 'sc_custom_center_outputs/'
    else:
        output_root_dir = ''
    if first_group == 'Actual Anatomical/ Injection Site Primary':
        output_dir = output_root_dir + 'sc_threshold_downsize/group_by_injection_site'
    else:
        output_dir = output_root_dir + 'sc_threshold_downsize/group_by_sc_zone'
    os.makedirs(output_dir, exist_ok=True)

    if use_custom_centers:
        source_root_dir = 'sc_custom_center_outputs/'
    else:
        source_root_dir = ''

    df = get_clean_df()
    case_ara_levels = get_case_ara_levels()

    group_by_values = pd.unique(df[first_group])
    for value in group_by_values:
        df_injection = df.loc[df[first_group] == value, :]
        value_dir = os.path.join(output_dir, value)
        os.makedirs(value_dir, exist_ok=True)
        for case_id, channel in df_injection.index.values:
            case_id_short = re.match('[A-Z]{2}[0-9]{6}-[0-9]{2}[A-D]', case_id).group()
            source_dir = source_root_dir + os.path.join('sc_threshold_downsize', case_id_short, 'threshold/channels', channel)
            ara_level_slides = case_ara_levels[case_id]
            ara_levels = sc_levels if not use_custom_centers else [sc_level for sc_level in sc_custom_centers.keys()]
            for sc_level in ara_levels:
                sc_level = str(sc_level)
                if sc_level not in ara_level_slides:
                    continue
                value_ara_level_dir = os.path.join(value_dir, sc_level.zfill(3))
                os.makedirs(value_ara_level_dir, exist_ok=True)
                slide = ara_level_slides[sc_level]
                source_name = '{}_ch{}-th.tif'.format(slide, channel)
                source_path = os.path.join(source_dir, source_name)
                assert os.path.isfile(source_path)
                shutil.copy(source_path, value_ara_level_dir)


if __name__ == '__main__':
    regroup_downsized_threshold()




