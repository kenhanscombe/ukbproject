import pandas as pd

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
    s = pd.read_csv(sample, sep=r'\s+', header=None, skiprows=[0, 1],
                    names=['id1', 'id2', 'mis'])

    w['exclude'] = 1

    f = pd.merge(f, w, how='left', left_on='fid', right_on='id', sort=False)
    s = pd.merge(s, w, how='left', left_on='id1', right_on='id', sort=False)

    f['exclude'] = f['exclude'].fillna(0).astype(int)
    s['exclude'] = s['exclude'].fillna(0).astype(int)

    # Include fam file phe column: 'redacted', 'dropout'
    f.loc[f['phe'].eq('redacted'), 'exclude'] = 1
    f.loc[f['phe'].eq('dropout'), 'exclude'] = 1

    # Add redacted/dropout fam exclude to sample exclude
    s = pd.merge(s[['id1', 'exclude']], f[['fid', 'exclude']],
                 how='left', left_on='id1', right_on='fid',
                 sort=False, suffixes=('_s', '_f'), validate='1:1')

    s.loc[(
        (s['exclude_s'] == 1) |
        (s['exclude_f'] == 1)), 'exclude'] = 1
    s.loc[(
        (s['exclude_s'] == 0) &
        (s['exclude_f'] == 0)), 'exclude'] = 0
    s['exclude'] = s['exclude'].astype(pd.Int64Dtype())

    # Add index
    f['index'] = [x + 1 for x in list(range(f.shape[0]))]
    s['index'] = [x + 1 for x in list(range(s.shape[0]))]

    f_exclude = f[['index', 'fid', 'exclude']]
    s_exclude = s[['index', 'id1', 'exclude']]

    return f_exclude, s_exclude
