import re
import pandas as pd


def remove_asterisk(df):
    for column in df.columns:
        try:
            df[column] = df[column].str.replace('\*', '').str.strip()
        except AttributeError:
            pass
    return df


def split_tracer_channel(df):
    df_tracer_channel = df['Tracers/Channel'].str.split('/', expand=True)
    df_tracer_channel.columns = ['Tracers', 'Channel']
    # make tracer lower case. remove leading numbered list characters. replace aav-tdtom as aav-tdtomato
    df_tracer_channel['Tracers'] = df_tracer_channel['Tracers'].str.strip()\
                                                               .str.lower()\
                                                               .str.replace('[0-9]\.[ ]*', '')\
                                                               .str.replace('tdtom$','tdtomato')
    # remove leading Ch in channel number
    df_tracer_channel['Channel'] = df_tracer_channel['Channel'].str.strip().str.lower().str.replace('ch', '')
    df = pd.concat([df, df_tracer_channel], axis=1)
    return df


def format_file_path(df):
    # modify file paths to linux system
    for path_column in ['Case Path (Thresholded Files)', 'Case path (osp files)']:
        df[path_column] = df[path_column].str.replace('\\', '/').str.replace('Z:', '/ifs/loni/faculty/dong/mcp')
    # if 'Case Path (Thresholded Files)' is missing, fill with 'Case path (osp files)'
    df['Case Path (Thresholded Files)'] = df['Case Path (Thresholded Files)'].fillna(df['Case path (osp files)'] + '/threshold/channels/' + df['Channel'])
    # if 'Case Path (osp files)' is missing, fill with 'Case path (Thresholded Files)'
    df['Case path (osp files)'] = df['Case path (osp files)'].fillna(df['Case Path (Thresholded Files)'].str.replace('/threshold/channels/[0-5]', ''))
    return df


def drop_invalid_rows(df):
    # drop rows where case id is NA or does not match case ID pattern
    # not enforcing case id ends with pattern due to such entries: SW121031-03B/A
    df = df.loc[df['Case ID'].notna() & df['Case ID'].str.match('[A-Z]{2}[0-9]{6}-[0-9]{2}[A-D]'), :]
    # if both 'Case Path (Thresholded Files)', 'Case path (osp files)' are missing values, drop rows
    df = df.loc[df['Case path (osp files)'].notna() | df['Case Path (Thresholded Files)'].notna(), :]
    # modify file paths to ini file system
    df = format_file_path(df)
    # check case id in index match case id in osp file path
    case_ids = df['Case ID'].apply(lambda x: re.match('[A-Z]{2}[0-9]{6}-[0-9]{2}[A-D]', x).group(0))
    osp_case_ids = df['Case path (osp files)'].str.split('/').str[-1].str.replace('SC_study_', '')
    matches = case_ids == osp_case_ids
    # remove rows with inconsistent case_id and osp file path
    if not matches.all():
        print('dropping \"Case ID\" inconsistent with \"Case path (osp files)\": {}'
              .format(df.loc[~matches.values, :]['Case ID'].values))
    df = df.loc[matches, :]
    # check threshold directory is valid combination of osp dir and channel number
    expected_threshold_dirs = df['Case path (osp files)'] + '/threshold/channels/' + df['Channel']
    matches = expected_threshold_dirs == df['Case Path (Thresholded Files)']
    # remove inconsistent rows
    if not matches.all():
        print('dropping \"Case ID\" with inconsistent \"Channel\" and \"Case Path (Thresholded Files)\": {}'
              .format(df.loc[~matches.values, :]['Case ID'].values))
    df = df.loc[matches, :]
    return df


def get_relevant_columns(df):
    relevant_columns = ['Case ID', 'Tracers', 'Channel', 'Cortex name with regional identifier',
                        'Actual Anatomical/ Injection Site', 'Actual Anatomical/ Injection Site Primary',
                        'Layer (injection site)', 'Target SC zones', 'Injection Site center ARA level (c)',
                        'ML (X)', 'AP (Y)', 'DV (Z)', 'Nissl Quality', 'Notes on SC labeling',
                        'Case Path (Thresholded Files)', 'Case path (osp files)']
    return df[relevant_columns]


def add_primary_injection(df):
    # SSp_tr is semantically the same as SSp-tr
    df['Actual Anatomical/ Injection Site'] = df['Actual Anatomical/ Injection Site'].str.replace('SSp_tr', 'SSp-tr')
    # for actual injection site, split the secondary information.
    # e.g. in VISp (med), med is secondary
    df['Actual Anatomical/ Injection Site Primary'] = df['Actual Anatomical/ Injection Site'].str.split().str.get(0).str.strip()
    return df


def remove_non_cortical_cases(df):
    non_cortical_regions = {'SNr', 'SC.l', 'SC.cl', 'SC.cm', 'SC.m', 'SC'}
    df = df.loc[~df['Actual Anatomical/ Injection Site Primary'].isin(non_cortical_regions), :]
    return df


def get_clean_df():
    df = pd.read_csv('ctx_sc_cases_06112020.csv', quotechar='\"', skipinitialspace=True, skiprows=4)
    # strip space in column names
    df.columns = df.columns.str.strip()
    # remove all asterisk character
    df = remove_asterisk(df)
    # split case and channel into separate columns
    df = split_tracer_channel(df)
    # remove invalid rows
    df = drop_invalid_rows(df)
    # add primary injection site column
    df = add_primary_injection(df)
    # retain only useful columns
    df = get_relevant_columns(df)
    # remove injection sites in non cortical regions
    df = remove_non_cortical_cases(df)
    # set case_id and channel multi index
    df = df.set_index(['Case ID', 'Channel'])
    # drop any duplicate multi index
    df = df.loc[~df.index.duplicated(), :]
    return df
