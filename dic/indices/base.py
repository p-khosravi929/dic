import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class BaseDroughtIndex(ABC):
    """Base class for all drought indices"""
    
    def __init__(self, data):
        self.data = data.copy()
        self._validate_data()
    
    def _validate_data(self):
        """Validate input data structure"""
        required_columns = ['year', 'month', 'precipitation']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"Data must contain columns: {required_columns}")
    
    @abstractmethod
    def calculate(self):
        """Calculate the drought index - to be implemented by subclasses"""
        pass
    
    @staticmethod
    def classify_drought(index_value):
        """
        Classify drought based on index value
        
        Parameters:
        index_value: drought index value
        
        Returns:
        drought_class: string classification
        """
        if pd.isna(index_value):
            return 'No Data'
        
        if index_value >= 2.0:
            return 'Extremely Wet'
        elif index_value >= 1.50:
            return 'Severe Wet'
        elif index_value >= 1.00:
            return 'Moderate Wet'
        elif index_value >= 0.50:
            return 'Mild Wet'
        elif index_value >= -0.49:
            return 'Normal'
        elif index_value >= -0.99:
            return 'Mild Drought'
        elif index_value >= -1.49:
            return 'Moderate Drought'
        elif index_value >= -1.99:
            return 'Severe Drought'
        else:
            return 'Extreme Drought'
