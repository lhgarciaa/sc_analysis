import os
import json
from collections import defaultdict
from parse_case_sheet import get_clean_df


df = get_clean_df()
# should be executed on ini machine
case_ara_levels = defaultdict(dict)
for case_channel in df.index.values:
    project_dir = df.loc[case_channel, 'Case path (osp files)']
    opairs_path = os.path.join(project_dir, 'opairs.lst')
    with open(opairs_path, 'r') as f:
        for l in f:
            case_slide, ara_level_str, _ = l.strip().split()
            case_ara_levels[case_channel[0]][int(ara_level_str)] = case_slide
with open('case_ara_levels.json', 'w') as f:
    json.dump(case_ara_levels, f)
