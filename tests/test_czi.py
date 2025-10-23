import unittest
import pandas as pd
import numpy as np
from dic.indices.czi import ChinaZIndex

class TestChinaZIndex(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        dates = pd.date_range('2000-01-01', '2005-12-31', freq='M')
        self.sample_data = pd.DataFrame({
            'year': dates.year,
            'month': dates.month,
            'precipitation': np.random.gamma(2, 2, len(dates))
        })
    
    def test_initialization(self):
        """Test CZI calculator initialization"""
        calculator = ChinaZIndex(self.sample_data)
        self.assertIsInstance(calculator, ChinaZIndex)
    
    def test_monthly_calculation(self):
        """Test monthly CZI calculation"""
        calculator = ChinaZIndex(self.sample_data)
        results = calculator.calculate_monthly_czi()
        
        self.assertIn('CZI', results.columns)
        self.assertIn('Drought_Class', results.columns)
        self.assertEqual(len(results), len(self.sample_data))
    
    def test_seasonal_calculation(self):
        """Test seasonal CZI calculation"""
        calculator = ChinaZIndex(self.sample_data)
        results = calculator.calculate_seasonal_czi()
        
        self.assertIn('CZI', results.columns)
        self.assertIn('Drought_Class', results.columns)
    
    def test_annual_calculation(self):
        """Test annual CZI calculation"""
        calculator = ChinaZIndex(self.sample_data)
        results = calculator.calculate_annual_czi()
        
        self.assertIn('CZI', results.columns)
        self.assertIn('Drought_Class', results.columns)

if __name__ == '__main__':
    unittest.main()
