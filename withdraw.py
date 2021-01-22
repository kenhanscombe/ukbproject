import pandas as pd
import glob
import re
from pathlib import Path


def withdraw_index(project_dir):
    """
    Writes indeces of samples to keep and remove.

    project_dir (str): Full path of the project directory
    """
    prj_dir = Path(project_dir)

    withdrawal_files = glob.glob(str(prj_dir / 'raw/w*csv'))
    fam_file = glob.glob(str(prj_dir / 'raw/*fam'))[0]
    sample_file = glob.glob(str(prj_dir / 'raw/*sample'))[0]

    wdfs = (pd.read_csv(w, header=None, names=[
            'id']) for w in withdrawal_files)
    wdfs_cat = pd.concat(wdfs)

    w = pd.DataFrame({'id': wdfs_cat.id.unique()})
    f = pd.read_csv(fam_file, sep=r'\s+', header=None,
                    names=['fid', 'iid', 'pid', 'mid', 'sex', 'phe'])
    s = pd.read_csv(sample_file, sep=r'\s+', skiprows=[1])

    w['exclude'] = 1

    f = pd.merge(f, w, how='left', left_on='fid', right_on='id', sort=False)
    s = pd.merge(s, w, how='left', left_on='ID_1', right_on='id', sort=False)

    f['exclude'] = f['exclude'].fillna(0).astype(int)
    s['exclude'] = s['exclude'].fillna(0).astype(int)

    # Include fam and sample negative ids
    f.loc[f['fid'].lt(0), 'exclude'] = 1
    s.loc[s['ID_1'].lt(0), 'exclude'] = 1

    # Add index
    f['index'] = [x + 1 for x in list(range(f.shape[0]))]
    s['index'] = [x + 1 for x in list(range(s.shape[0]))]

    f_exclude = f[['index', 'fid', 'exclude']]
    s_exclude = s[['index', 'ID_1', 'exclude']]

    # Log info
    log_info = {'project_id': re.sub('ukb|_.*$', '', str(project_dir)),
                'withdrawal_n': w.shape[0],
                'fam_n': f.shape[0],
                'fam_negative_n': f.loc[f['fid'].lt(0)].shape[0],
                'fam_in_withdrawal_n': sum(f['fid'].isin(w['id']).tolist()),
                'fam_exclusion_n': f.loc[f['exclude'].eq(1)].shape[0],
                'sample_n': s.shape[0],
                'sample_negative_n': s.loc[s['ID_1'].lt(0)].shape[0],
                'sample_in_withdrawal_n': sum(s['ID_1'].isin(w['id']).tolist()),
                'sample_exclusion_n': s.loc[s['exclude'].eq(1)].shape[0]}

    return f_exclude, s_exclude, log_info
