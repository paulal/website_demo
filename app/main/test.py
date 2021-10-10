"""Unit tests for demo website functions in helpers.py"""

import unittest
from unittest.mock import patch, Mock

import pandas as pd

from helpers import get_rda, get_nutrition_values_of_foods, solve_for_optimal_foods


class HelperTest(unittest.TestCase):
    def test_get_rda(self):
        """Get the correct rda values from the csv"""
        rda_data = [["VITA","A-vitamiini RE","UG",900,901,902,903,904,600,700,701,702,703,704,2500],
                    ["VITD","D-vitamiini μg","UG",10,11,12,13,20,14,15,16,17,18,21,80],
                    ["VITE","E-vitamiini α–TE","MG",11,12,13,14,15,7,8,9,10,11,12,250]]
        rda_df = pd.DataFrame(data=rda_data, columns=["EUFDNAME", "name", "unit", "mnuori", "maikuinen", "mkeski", "miäkäs", "mvanha", "npieni","nnuori", "naikuinen", "nkeski", "niäkäs", "nvanha", "max"])
        with patch("helpers.pd.read_csv") as csv_mock:
            csv_mock.return_value = rda_df
            actual = get_rda("mnuori")

        self.assertEqual(actual.loc[0, 'EUFDNAME'], 'vita')
        self.assertEqual(actual.loc[0, 'target'], 900)
        self.assertEqual(actual.loc[1, 'target'], 10)
        self.assertEqual(actual.loc[2, 'max'], 250)
        

if __name__ == '__main__':
    unittest.main(verbosity=2)