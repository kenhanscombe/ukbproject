import pandas as pd
import re
from pathlib import Path

# Each project has (with project-specific ids) :
# - w*.csv withdrawals file(s)
# - fam file (which correspond to the bed/bim files)
# - sample file (which corresponds to bgen/bgen.bgi files)
# (- phenotype data file)

# TODO: Find exclude/redacted/dropout fam ids in sample ids
# TODO: Confirm: phenotype (file) can be smaller than fam/sample
# TODO: Confirm: fam to bed (and sample to bgen) size correspondence
# TODO: Can I delete from bed/bgen only (can't delete in fam/sample?)


def withdraw_index(withdraw, fam, sample):
    """Writes indeces of samples to keep and remove

    withdraw (str): Path to the withdrawals file
    fam (str): Path to the fam file
    sample (str): Path to the sample file
    """
    w = pd.read_csv(withdraw, header=None, names=['id'])
    f = pd.read_csv(fam, sep=r'\s+', header=None,
                    names=['fid', 'iid', 'pid', 'mid', 'sex', 'phe'])
    s = pd.read_csv(sample, sep=r'\s+', skiprows=[1])

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
    f_path = Path(fam)
    project_dir = f_path.absolute().parent.parent.name

    log_info = {'project_id': re.sub('ukb|_.*$', '', project_dir),
                'withdrawal_n': w.shape[0],
                'fam_n': f.shape[0],
                'fam_negative_n': f.loc[f['fid'].lt(0)].shape[0],
                'fam_in_withdrawal_n': sum(f['fid'].isin(w['id']).tolist()),
                'fam_exclusion_n': f.loc[f['excluion'].eq(1)].shape[0],
                'sample_n': s.shape[0],
                'sample_negative_n': s.loc[s['fid'].lt(0)].shape[0],
                'sample_in_withdrawal_n': sum(s['ID_1'].isin(w['id']).tolist()),
                'sample_exclusion_n': s.loc[s['excluion'].eq(1)].shape[0]}

    return f_exclude, s_exclude, log_info
