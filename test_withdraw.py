import unittest
import withdraw
import tempfile
import pandas as pd
import numpy as np

from pathlib import Path
from random import randint, sample, choices


class TestWithdraw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.p = Path(cls.temp_dir.name)

        # test samples
        fam_size = 100
        ids = sample([x + 1 for x in range(1000, 2000)], k=fam_size)
        sex = choices([1, 2], k=100)

        # test withdrawal file
        cls.withdraw_path = cls.p.absolute() / 'wPROJECT_20200101.csv'
        withdraw_ids = sample(ids, round(fam_size * 0.1))
        withdraw_df = pd.DataFrame(withdraw_ids)
        withdraw_df.to_csv(cls.withdraw_path, index=False, header=False)

        # test fam file
        cls.fam_path = cls.p.absolute() / 'ukbPROJECT.fam'
        fam_df = pd.DataFrame({
            'fid': ids,
            'iid': ids,
            'pid': 0,
            'mid': 0,
            'sex': sex,
            'phe': np.random.choice(['Batch', 'dropout', 'redacted'],
                                    fam_size, p=[.7, .2, .1])})

        fam_df.to_csv(cls.fam_path, sep=' ', index=False, header=False)

        # test sample file
        cls.sample_path = cls.p.absolute() / 'ukbPROJECT.sample'
        sample_ids = sample(ids, round(fam_size * 0.95))
        sample_df = pd.DataFrame({
            'ID_1': [0] + sample_ids,
            'ID_2': 0,
            'missing': 0})

        sample_df.to_csv(cls.sample_path, sep=' ', index=False)

        cls.f_exclude, cls.s_exclude, cls.log_info = withdraw.withdraw_index(
            withdraw=cls.withdraw_path,
            fam=cls.fam_path,
            sample=cls.sample_path)

    @ classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_exclusions(self):
        """Withdrawal exclusions are non empty"""
        self.assertTrue(not self.f_exclude.empty)
        self.assertTrue(not self.s_exclude.empty)
        self.assertTrue(isinstance(self.log_info, dict) &
                        bool(self.log_info))

    def test_counts(self):
        """Total withdrawal exclusions are the sum of negative ids and
        withdrawal ids in sample information file"""
        self.assertEqual(
            self.log_info['fam_negative_n'] +
            self.log_info['fam_in_withdrawal_n'],
            self.log_info['fam_exclusion_n'])
        self.assertEqual(
            self.log_info['sample_negative_n'] +
            self.log_info['sample_in_withdrawal_n'],
            self.log_info['sample_exclusion_n'])


if __name__ == '__main__':
    unittest.main()
