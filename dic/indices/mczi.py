import pandas as pd
import numpy as np
from scipy import stats
from .base import BaseDroughtIndex

class ModifiedChinaZIndex(BaseDroughtIndex):
    """
    Modified China Z-Index (MCZI) calculator
    Uses median instead of mean for better performance with skewed data
    """
    
    def __init__(self, data):
        """
        Initialize Modified CZI calculator
        
        Args:
            data: DataFrame with 'year', 'month', 'precipitation' columns
        """
        super().__init__(data)
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess the input data"""
        self.data['date'] = pd.to_datetime(
            self.data[['year', 'month']].assign(day=1)
        )
        self.data = self.data.set_index('date')
    
    def calculate_mczi(self, precipitation_series):
        """
        Calculate Modified China Z-Index (MCZI) for a given precipitation series
        
        Parameters:
            precipitation_series: pandas Series of precipitation values
            
        Returns:
            mczi_values: pandas Series of MCZI values
        """
        precip = precipitation_series.dropna()
        
        if len(precip) < 2:
            return pd.Series([np.nan] * len(precipitation_series), 
                           index=precipitation_series.index)
        
        # Use median instead of mean (key modification from CZI)
        median_precip = np.median(precip)
        std_precip = np.std(precip, ddof=1)
        
        if std_precip == 0:
            return pd.Series([0] * len(precipitation_series), 
                           index=precipitation_series.index)
        
        n = len(precip)
        
        # Calculate skewness using median
        skewness = (np.sum((precip - median_precip) ** 3) / n) / (std_precip ** 3)
        
        mczi_values = []
        
        for x in precipitation_series:
            if pd.isna(x):
                mczi_values.append(np.nan)
                continue
            
            # Calculate Z-score using median
            z = (x - median_precip) / std_precip
            
            if skewness == 0:
                mcz = z
            else:
                # Apply Wilson-Hilferty transformation with median-based calculation
                term1 = (6 / skewness) * ((skewness / 2) * z + 1) ** (1/3)
                term2 = (6 / skewness) + (skewness / 6)
                mcz = term1 - term2
            
            mczi_values.append(mcz)
        
        return pd.Series(mczi_values, index=precipitation_series.index)
    
    def calculate_monthly_mczi(self):
        """Calculate monthly MCZI values"""
        monthly_mczi = self.calculate_mczi(self.data['precipitation'])
        
        result = pd.DataFrame({
            'year': self.data.index.year,
            'month': self.data.index.month,
            'precipitation': self.data['precipitation'],
            'MCZI': monthly_mczi
        })
        
        result['Drought_Class'] = result['MCZI'].apply(self.classify_drought)
        return result
    
    def calculate_seasonal_mczi(self):
        """Calculate seasonal MCZI values"""
        seasons = {
            1: 'Winter', 2: 'Winter', 3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer', 9: 'Fall', 10: 'Fall', 
            11: 'Fall', 12: 'Winter'
        }
        
        self.data['season'] = self.data.index.month.map(seasons)
        self.data['year_season'] = self.data.index.year.astype(str) + '_' + self.data['season']
        
        # Adjust for winter season (Dec belongs to next year's winter)
        winter_mask = self.data.index.month == 12
        self.data.loc[winter_mask, 'year_season'] = (self.data.index[winter_mask].year + 1).astype(str) + '_Winter'
        
        seasonal_precip = self.data.groupby('year_season')['precipitation'].sum()
        seasonal_mczi = self.calculate_mczi(seasonal_precip)
        
        result_data = []
        for idx, mcz_value in seasonal_mczi.items():
            year, season = idx.split('_')
            result_year = int(year) if season != 'Winter' else int(year) - 1
            
            result_data.append({
                'year': result_year,
                'season': season,
                'precipitation': seasonal_precip[idx],
                'MCZI': mcz_value,
                'Drought_Class': self.classify_drought(mcz_value)
            })
        
        return pd.DataFrame(result_data)
    
    def calculate_annual_mczi(self):
        """Calculate annual MCZI values"""
        annual_data = self.data.groupby(self.data.index.year)['precipitation'].sum().reset_index()
        annual_data.columns = ['year', 'precipitation']
        
        annual_mczi = self.calculate_mczi(annual_data['precipitation'])
        annual_data['MCZI'] = annual_mczi.values
        annual_data['Drought_Class'] = annual_data['MCZI'].apply(self.classify_drought)
        
        return annual_data
    
    def compare_with_czi(self, czi_calculator):
        """
        Compare MCZI with CZI results
        
        Args:
            czi_calculator: Instance of ChinaZIndex class
            
        Returns:
            DataFrame with comparison results
        """
        mczi_monthly = self.calculate_monthly_mczi()
        czi_monthly = czi_calculator.calculate_monthly_czi()
        
        comparison_df = mczi_monthly[['year', 'month', 'precipitation', 'MCZI', 'Drought_Class']].copy()
        comparison_df['CZI'] = czi_monthly['CZI']
        comparison_df['CZI_Drought_Class'] = czi_monthly['Drought_Class']
        comparison_df['Difference'] = comparison_df['MCZI'] - comparison_df['CZI']
        comparison_df['Class_Agreement'] = comparison_df['Drought_Class'] == comparison_df['CZI_Drought_Class']
        
        return comparison_df
    
    def calculate(self, frequency='monthly'):
        """
        Main calculate method for different frequencies
        
        Parameters:
            frequency: 'monthly', 'seasonal', or 'annual'
            
        Returns:
            DataFrame with results
        """
        if frequency == 'monthly':
            return self.calculate_monthly_mczi()
        elif frequency == 'seasonal':
            return self.calculate_seasonal_mczi()
        elif frequency == 'annual':
            return self.calculate_annual_mczi()
        else:
            raise ValueError("Frequency must be 'monthly', 'seasonal', or 'annual'")
