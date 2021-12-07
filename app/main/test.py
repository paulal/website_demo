"""Unit tests for demo website functions in helpers.py"""

import unittest
from unittest.mock import patch, Mock
import datetime

import pandas as pd

from helpers import get_rda, get_nutrition_values_of_foods, solve_for_optimal_foods, \
     get_daily_values, get_bear_length, get_buy_and_sell_dates


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
    
    def test_get_daily_values(self):
        """Get the first and only the first value for each day"""
        data = [
            [
              1638396252313,
              50416.662545018866
            ],
            [
              1638399794129,
              50473.418293502924
            ],
            [
              1638403476369,
              50506.910551023844
            ],
            [
              1638407244512,
              50299.432691457565
            ],
            [
              1638486031753,
              50349.270930451385
            ],
            [
              1638489808780,
              49974.160510668
            ]
          ]
        actual = get_daily_values(data)
        
        self.assertEqual(actual, [[datetime.date(2021, 12, 1), 50416.662545018866],
                                  [datetime.date(2021, 12, 2), 50506.910551023844],
                                  [datetime.date(2021, 12, 3), 49974.160510668]])
    
    def test_get_bear_length(self):
        prices = [[datetime.date(2021, 3, 1), 49493198447.75872],
                  [datetime.date(2021, 3, 2), 51389538313.89711],
                  [datetime.date(2021, 3, 3), 44001647654.76413],
                  [datetime.date(2021, 3, 4), 48996964876.455315],
                  [datetime.date(2021, 3, 5), 50768369805.09877],
                  [datetime.date(2021, 3, 6), 47264632660.507416],
                  [datetime.date(2021, 3, 7), 34767011233.68442]]
        actual = get_bear_length(prices)
        self.assertEqual(actual, 2)
    
    def test_get_buy_and_sell_dates(self):
        prices = [[datetime.date(2021, 3, 1), 49493198447.75872],
                  [datetime.date(2021, 3, 2), 51389538313.89711],
                  [datetime.date(2021, 3, 3), 44001647654.76413],
                  [datetime.date(2021, 3, 4), 48996964876.455315],
                  [datetime.date(2021, 3, 5), 50768369805.09877],
                  [datetime.date(2021, 3, 6), 47264632660.507416],
                  [datetime.date(2021, 3, 7), 34767011233.68442],
                  [datetime.date(2021, 3, 7), 34767011233.68442],
                  [datetime.date(2021, 3, 8), 38614211636.00619]]
        actual = get_buy_and_sell_dates(prices)
        self.assertEqual(actual, (datetime.date(2021, 3, 3), datetime.date(2021, 3, 5)))
        

if __name__ == '__main__':
    unittest.main(verbosity=2)