import pytest
import withdraw
import pandas as pd
import numpy as np

from random import sample, choices


@pytest.fixture(scope="class")
def example_data(tmp_path_factory, request):
    d = tmp_path_factory.mktemp('project')
    raw = d / 'raw'
    raw.mkdir()

    # test samples
    fam_size = 100
    ids = sample([x + 1 for x in range(1000, 2000)], k=fam_size)
    sex = choices([1, 2], k=100)

    # withdrawal data
    withdraw_path = str(raw / 'wPROJECT_20200101.csv')
    withdraw_ids = sample(ids, round(fam_size * 0.1))
    withdraw_df = pd.DataFrame(withdraw_ids)
    withdraw_df.to_csv(withdraw_path, index=False, header=False)

    # fam data
    fam_path = str(raw / 'ukbPROJECT.fam')
    fam_df = pd.DataFrame({
        'fid': ids,
        'iid': ids,
        'pid': 0,
        'mid': 0,
        'sex': sex,
        'phe': np.random.choice(['Batch', 'dropout', 'redacted'],
                                fam_size, p=[.7, .2, .1])})
    fam_df.to_csv(fam_path, sep=' ', index=False, header=False)

    # sample data
    sample_path = str(raw / 'ukbPROJECT.sample')
    sample_ids = sample(ids, round(fam_size * 0.95))
    sample_df = pd.DataFrame({
        'ID_1': [0] + sample_ids,
        'ID_2': 0,
        'missing': 0})
    sample_df.to_csv(sample_path, sep=' ', index=False)

    request.cls.f_exclude, request.cls.s_exclude, request.cls.log_info = \
        withdraw.withdraw_index(project_dir=str(d))


@pytest.mark.usefixtures('example_data')
class TestWithdrawIndex:
    def test_exclusions(self):
        """Withdrawal exclusions are non empty"""
        assert (not self.f_exclude.empty)
        assert (not self.s_exclude.empty)
        assert (isinstance(self.log_info, dict) &
                bool(self.log_info))

    def test_counts(self):
        """Total withdrawal exclusions are the sum of negative ids and
        withdrawal ids in sample information file"""
        assert self.log_info['fam_negative_n'] + \
            self.log_info['fam_in_withdrawal_n'] == \
            self.log_info['fam_exclusion_n']

        assert self.log_info['sample_negative_n'] + \
            self.log_info['sample_in_withdrawal_n'] == \
            self.log_info['sample_exclusion_n']
