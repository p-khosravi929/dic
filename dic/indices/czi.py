import pandas as pd
import numpy as np
from .base import BaseDroughtIndex

class ChinaZIndex(BaseDroughtIndex):
    """
    China Z-Index (CZI) calculator using Wilson-Hilferty cube root transformation
    
    References:
    - Equation 3.1 and 3.2 from drought Index.pdf
    """
    
    def __init__(self, data):
        super().__init__(data)
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess the input data"""
        self.data['date'] = pd.to_datetime(self.data[['year', 'month']].assign(day=1))
        self.data = self.data.set_index('date')
    
    def calculate_czi(self, precipitation_series):
        """
        Calculate China Z-Index (CZI) for a given precipitation series
        
        Parameters:
        precipitation_series: pandas Series of precipitation values
        
        Returns:
        cz_values: pandas Series of CZI values
        """
        precip = precipitation_series.dropna()
        
        if len(precip) < 2:
            return pd.Series([np.nan] * len(precipitation_series), index=precipitation_series.index)
        
        mean_precip = np.mean(precip)
        std_precip = np.std(precip, ddof=1)
        
        if std_precip == 0:
            return pd.Series([0] * len(precipitation_series), index=precipitation_series.index)
        
        n = len(precip)
        skewness = (np.sum((precip - mean_precip) ** 3) / n) / (std_precip ** 3)
        
        cz_values = []
        for x in precipitation_series:
            if pd.isna(x):
                cz_values.append(np.nan)
                continue
                
            z = (x - mean_precip) / std_precip
            
            if skewness == 0:
                cz = z
            else:
                term1 = (6 / skewness) * ((skewness / 2) * z + 1) ** (1/3)
                term2 = (6 / skewness) + (skewness / 6)
                cz = term1 - term2
            
            cz_values.append(cz)
        
        return pd.Series(cz_values, index=precipitation_series.index)
    
    def calculate_monthly_czi(self):
        """Calculate monthly CZI values"""
        monthly_czi = self.calculate_czi(self.data['precipitation'])
        result = pd.DataFrame({
            'year': self.data.index.year,
            'month': self.data.index.month,
            'precipitation': self.data['precipitation'],
            'CZI': monthly_czi
        })
        result['Drought_Class'] = result['CZI'].apply(self.classify_drought)
        return result
    
    def calculate_seasonal_czi(self):
        """Calculate seasonal CZI values"""
        seasons = {
            1: 'Winter', 2: 'Winter', 3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer', 9: 'Fall', 10: 'Fall', 11: 'Fall', 12: 'Winter'
        }
        
        self.data['season'] = self.data.index.month.map(seasons)
        self.data['year_season'] = self.data.index.year.astype(str) + '_' + self.data['season']
        
        winter_mask = self.data.index.month == 12
        self.data.loc[winter_mask, 'year_season'] = (self.data.index[winter_mask].year + 1).astype(str) + '_Winter'
        
        seasonal_precip = self.data.groupby('year_season')['precipitation'].sum()
        seasonal_czi = self.calculate_czi(seasonal_precip)
        
        result_data = []
        for idx, cz_value in seasonal_czi.items():
            year, season = idx.split('_')
            result_year = int(year) if season != 'Winter' else int(year) - 1
            result_data.append({
                'year': result_year,
                'season': season,
                'precipitation': seasonal_precip[idx],
                'CZI': cz_value,
                'Drought_Class': self.classify_drought(cz_value)
            })
        
        return pd.DataFrame(result_data)
    
    def calculate_annual_czi(self):
        """Calculate annual CZI values"""
        annual_data = self.data.groupby(self.data.index.year)['precipitation'].sum().reset_index()
        annual_data.columns = ['year', 'precipitation']
        
        annual_czi = self.calculate_czi(annual_data['precipitation'])
        annual_data['CZI'] = annual_czi.values
        annual_data['Drought_Class'] = annual_data['CZI'].apply(self.classify_drought)
        
        return annual_data
    
    def calculate(self, frequency='monthly'):
        """
        Main calculate method for different frequencies
        
        Parameters:
        frequency: 'monthly', 'seasonal', or 'annual'
        
        Returns:
        DataFrame with results
        """
        if frequency == 'monthly':
            return self.calculate_monthly_czi()
        elif frequency == 'seasonal':
            return self.calculate_seasonal_czi()
        elif frequency == 'annual':
            return self.calculate_annual_czi()
        else:
            raise ValueError("Frequency must be 'monthly', 'seasonal', or 'annual'")
