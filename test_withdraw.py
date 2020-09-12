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

    @ classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_withdraw_index(self):
        """Is a non-empty dataframe"""
        f_exclude, s_exclude = withdraw.withdraw_index(
            withdraw=self.withdraw_path,
            fam=self.fam_path,
            sample=self.sample_path
        )

        print('fam exclude file:', f_exclude.shape)
        print(f_exclude.head())
        print(f_exclude['exclude'].value_counts(), '\n')

        print('sample exclude file:', s_exclude.shape)
        print(s_exclude.head())
        print(s_exclude['exclude'].value_counts(), '\n')

        # path exists (handle error, test its caught)
        # is a pd.DataFrame
        # is not empty
        # withdrawal ids are in fam/ sample
        # self.assertIsInstance(w, pd.DataFrame)
        # self.assertIsInstance(f, pd.DataFrame)
        # self.assertIsInstance(s, pd.DataFrame)
        # self.assertTrue(not w.empty)
        # self.assertTrue(not f.empty)
        # self.assertTrue(not s.empty)


if __name__ == '__main__':
    unittest.main()
