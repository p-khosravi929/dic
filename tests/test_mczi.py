import unittest
import pandas as pd
import numpy as np
from scipy import stats
from dic.indices.mczi import ModifiedChinaZIndex
from dic.indices.czi import ChinaZIndex

class TestModifiedChinaZIndex(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        dates = pd.date_range('2000-01-01', '2002-12-31', freq='M')
        self.sample_data = pd.DataFrame({
            'year': dates.year,
            'month': dates.month,
            'precipitation': np.random.gamma(2, 2, len(dates))
        })
    
    def test_initialization(self):
        """Test Modified CZI calculator initialization"""
        calculator = ModifiedChinaZIndex(self.sample_data)
        self.assertIsInstance(calculator, ModifiedChinaZIndex)
    
    def test_monthly_calculation(self):
        """Test monthly MCZI calculation"""
        calculator = ModifiedChinaZIndex(self.sample_data)
        results = calculator.calculate_monthly_mczi()
        
        # Check required columns
        required_columns = ['year', 'month', 'precipitation', 'MCZI', 'Drought_Class']
        for col in required_columns:
            self.assertIn(col, results.columns)
        
        # Check data length
        self.assertEqual(len(results), len(self.sample_data))
        
        # Check that MCZI values are calculated
        self.assertFalse(results['MCZI'].isna().all())
    
    def test_seasonal_calculation(self):
        """Test seasonal MCZI calculation"""
        calculator = ModifiedChinaZIndex(self.sample_data)
        results = calculator.calculate_seasonal_mczi()
        
        self.assertIn('MCZI', results.columns)
        self.assertIn('Drought_Class', results.columns)
        self.assertIn('season', results.columns)
        
        # Should have 4 seasons per year
        expected_seasons = 3 * 4  # 3 years * 4 seasons
        self.assertEqual(len(results), expected_seasons)
    
    def test_annual_calculation(self):
        """Test annual MCZI calculation"""
        calculator = ModifiedChinaZIndex(self.sample_data)
        results = calculator.calculate_annual_mczi()
        
        self.assertIn('MCZI', results.columns)
        self.assertIn('Drought_Class', results.columns)
        
        # Should have 3 annual records
        self.assertEqual(len(results), 3)
    
    def test_median_usage(self):
        """Test that MCZI uses median instead of mean"""
        # Create data with extreme outliers
        test_data = pd.DataFrame({
            'year': [2000] * 12,
            'month': range(1, 13),
            'precipitation': [10, 12, 8, 9, 11, 13, 7, 14, 10, 12, 9, 100]  # Extreme value at end
        })
        
        calculator = ModifiedChinaZIndex(test_data)
        mczi_results = calculator.calculate_monthly_mczi()
        
        # MCZI should be less affected by the extreme value
        self.assertFalse(mczi_results['MCZI'].isna().all())
    
    def test_comparison_with_czi(self):
        """Test comparison method with CZI"""
        mczi_calculator = ModifiedChinaZIndex(self.sample_data)
        czi_calculator = ChinaZIndex(self.sample_data)
        
        comparison_results = mczi_calculator.compare_with_czi(czi_calculator)
        
        # Check comparison columns
        comparison_columns = ['year', 'month', 'precipitation', 'MCZI', 'Drought_Class', 
                             'CZI', 'CZI_Drought_Class', 'Difference', 'Class_Agreement']
        
        for col in comparison_columns:
            self.assertIn(col, comparison_results.columns)
    
    def test_drought_classification(self):
        """Test MCZI drought classification"""
        calculator = ModifiedChinaZIndex(self.sample_data)
        
        test_cases = [
            (2.5, 'Extremely Wet'),
            (1.75, 'Severe Wet'),
            (1.25, 'Moderate Wet'),
            (0.75, 'Mild Wet'),
            (0.0, 'Normal'),
            (-0.75, 'Mild Drought'),
            (-1.25, 'Moderate Drought'),
            (-1.75, 'Severe Drought'),
            (-2.5, 'Extreme Drought')
        ]
        
        for mczi_value, expected_class in test_cases:
            classified = calculator.classify_drought(mczi_value)
            self.assertEqual(classified, expected_class)
    
    def test_main_calculate_method(self):
        """Test main calculate method with different frequencies"""
        calculator = ModifiedChinaZIndex(self.sample_data)
        
        # Test monthly frequency
        monthly_results = calculator.calculate('monthly')
        self.assertIn('MCZI', monthly_results.columns)
        
        # Test seasonal frequency
        seasonal_results = calculator.calculate('seasonal')
        self.assertIn('MCZI', seasonal_results.columns)
        
        # Test annual frequency
        annual_results = calculator.calculate('annual')
        self.assertIn('MCZI', annual_results.columns)
        
        # Test invalid frequency
        with self.assertRaises(ValueError):
            calculator.calculate('invalid')

if __name__ == '__main__':
    unittest.main()
