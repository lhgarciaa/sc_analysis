import os
import time


def time_stamp(output_format='Y-%m-%d-%H:%M:%S'):
    return time.strftime(output_format, time.localtime())


sc_levels = range(83, 105)


sc_codecs = {
    '254:121:255': 'Scig_b', '254:132:253': 'SCs_zo', '254:132:254': 'SCs_sg', '254:132:255': 'SCs_op',
    '254:133:249': 'SCm_dw', '254:133:250': 'SCm_ig', '254:133:251': 'SCM_ig-c', '254:133:252': 'SCM_ig-b',
    '254:133:253': 'SCM_ig-a', '254:133:254': 'SCm_iw', '254:133:255': 'SCm_dg'
}

version = 'v1.0'


def plots_out_dir():
    d = os.path.join('plots', version)
    os.makedirs(d, exist_ok=True)
    return d
