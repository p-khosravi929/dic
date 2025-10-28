import unittest
import pandas as pd
import numpy as np
from dic.indices.ci import CompositeIndex

class TestCompositeIndex(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        dates = pd.date_range('2000-01-01', '2002-12-31', freq='M')
        self.sample_data = pd.DataFrame({
            'year': dates.year,
            'month': dates.month,
            'precipitation': np.random.gamma(2, 2, len(dates))
        })
    
    def test_initialization(self):
        """Test Composite Index calculator initialization"""
        calculator = CompositeIndex(self.sample_data)
        self.assertIsInstance(calculator, CompositeIndex)
        self.assertEqual(calculator.coefficients['a'], 0.47)
        self.assertEqual(calculator.coefficients['b'], 0.36)
        self.assertEqual(calculator.coefficients['c'], 0.96)
    
    def test_composite_index_calculation(self):
        """Test Composite Index calculation"""
        calculator = CompositeIndex(self.sample_data)
        results = calculator.calculate_composite_index()
        
        # Check required columns
        required_columns = ['year', 'month', 'precipitation', 'SPI_1month', 
                           'SPI_3month', 'Moisture_Index', 'Composite_Index', 'Drought_Class']
        for col in required_columns:
            self.assertIn(col, results.columns)
        
        # Check data length
        self.assertEqual(len(results), len(self.sample_data))
    
    def test_drought_classification(self):
        """Test CI drought classification"""
        calculator = CompositeIndex(self.sample_data)
        
        test_cases = [
            (-0.3, 'Normal'),
            (-0.8, 'Mild Drought'),
            (-1.5, 'Moderate Drought'),
            (-2.0, 'Severe Drought'),
            (-2.5, 'Extreme Drought')
        ]
        
        for ci_value, expected_class in test_cases:
            classified = calculator.classify_ci_drought([ci_value])[0]
            self.assertEqual(classified, expected_class)
    
    def test_moisture_index_calculation(self):
        """Test moisture index calculation"""
        calculator = CompositeIndex(self.sample_data)
        moisture_index = calculator.calculate_moisture_index()
        
        self.assertEqual(len(moisture_index), len(self.sample_data))
        self.assertTrue(all(moisture_index <= 1))  # Moisture index should be <= 1
    
    def test_main_calculate_method(self):
        """Test main calculate method"""
        calculator = CompositeIndex(self.sample_data)
        results = calculator.calculate('monthly')
        
        self.assertIn('Composite_Index', results.columns)
        self.assertIn('Drought_Class', results.columns)

if __name__ == '__main__':
    unittest.main()
