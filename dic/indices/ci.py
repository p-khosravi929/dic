import pandas as pd
import numpy as np
from scipy import stats
from .base import BaseDroughtIndex

class CompositeIndex(BaseDroughtIndex):
    """
    Composite Index (CI) calculator 
    Combines SPI and moisture index components
    
    References:
    - Equation 3.3 and 3.4 from drought Index.pdf
    - Zhang et al. (2006)
    """
    
    def __init__(self, data, temperature_data=None):
        """
        Initialize Composite Index calculator
        
        Args:
            data: DataFrame with 'year', 'month', 'precipitation' columns
            temperature_data: DataFrame with temperature data (optional)
        """
        super().__init__(data)
        self.temperature_data = temperature_data
        self.coefficients = {'a': 0.47, 'b': 0.36, 'c': 0.96}
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess the input data"""
        self.data['date'] = pd.to_datetime(
            self.data[['year', 'month']].assign(day=1)
        )
        self.data = self.data.set_index('date')
    
    def calculate_spi(self, timescale, precipitation_series):
        """
        Calculate SPI for given timescale
        
        Args:
            timescale: time scale in months (1, 3, 6, 12, etc.)
            precipitation_series: pandas Series of precipitation values
            
        Returns:
            spi_values: pandas Series of SPI values
        """
        precip = precipitation_series.dropna()
        
        if len(precip) < timescale:
            return pd.Series([np.nan] * len(precipitation_series), 
                           index=precipitation_series.index)
        
        # Calculate rolling sum
        rolling_sum = precip.rolling(window=timescale, min_periods=timescale).sum()
        
        spi_values = []
        for i in range(len(rolling_sum)):
            if i < timescale - 1:
                spi_values.append(np.nan)
            else:
                # Use available data for distribution fitting
                sample_data = rolling_sum.iloc[max(0, i-359):i+1].dropna()
                
                if len(sample_data) > 1:
                    # Fit gamma distribution
                    params = stats.gamma.fit(sample_data, floc=0)
                    # Calculate cumulative probability
                    prob = stats.gamma.cdf(rolling_sum.iloc[i], *params)
                    # Convert to SPI (standard normal)
                    spi = stats.norm.ppf(prob)
                    spi_values.append(spi)
                else:
                    spi_values.append(np.nan)
        
        return pd.Series(spi_values, index=precipitation_series.index)
    
    def calculate_potential_evapotranspiration(self):
        """
        Calculate Potential Evapotranspiration using simplified method
        """
        # Simplified PET calculation - you can enhance this with proper temperature data
        if self.temperature_data is not None:
            # If temperature data available, use Hargreaves method
            self.data['PET'] = 0.0023 * 0.408 * self.temperature_data['temperature'] * 50
        else:
            # Simplified approach based on precipitation
            self.data['PET'] = self.data['precipitation'] * 0.7
        
        return self.data['PET']
    
    def calculate_moisture_index(self):
        """
        Calculate monthly moisture index M₃₀ = (P - PE) / P
        
        Returns:
            moisture_index: pandas Series of moisture index values
        """
        pet = self.calculate_potential_evapotranspiration()
        precipitation = self.data['precipitation']
        
        # Avoid division by zero
        moisture_index = np.where(
            precipitation > 0,
            (precipitation - pet) / precipitation,
            0  # Default value when precipitation is 0
        )
        
        return pd.Series(moisture_index, index=self.data.index)
    
    def calculate_composite_index(self):
        """
        Calculate Composite Index (CI) = aZ₃₀ + bZ₉₀ + cM₃₀
        
        Returns:
            DataFrame with CI results
        """
        # Calculate required components
        spi_1month = self.calculate_spi(1, self.data['precipitation'])  # Z₃₀
        spi_3month = self.calculate_spi(3, self.data['precipitation'])  # Z₉₀
        moisture_index = self.calculate_moisture_index()  # M₃₀
        
        # Apply coefficients and calculate CI
        ci_values = (
            self.coefficients['a'] * np.array(spi_1month) +
            self.coefficients['b'] * np.array(spi_3month) + 
            self.coefficients['c'] * np.array(moisture_index)
        )
        
        # Create result DataFrame
        result_df = self.data.reset_index()[['year', 'month', 'precipitation']].copy()
        result_df['SPI_1month'] = spi_1month.values
        result_df['SPI_3month'] = spi_3month.values
        result_df['Moisture_Index'] = moisture_index.values
        result_df['Composite_Index'] = ci_values
        result_df['Drought_Class'] = self.classify_ci_drought(ci_values)
        
        return result_df
    
    def classify_ci_drought(self, ci_values):
        """
        Classify drought based on CI values (from Table 3.1 in PDF)
        
        Args:
            ci_values: array of CI values
            
        Returns:
            list of drought classifications
        """
        categories = []
        for ci in ci_values:
            if np.isnan(ci):
                categories.append('No Data')
            elif ci > -0.6:
                categories.append('Normal')
            elif ci >= -1.2:
                categories.append('Mild Drought')
            elif ci >= -1.8:
                categories.append('Moderate Drought')
            elif ci >= -2.4:
                categories.append('Severe Drought')
            else:
                categories.append('Extreme Drought')
        return categories
    
    def calculate(self, frequency='monthly'):
        """
        Main calculate method
        
        Args:
            frequency: calculation frequency ('monthly')
            
        Returns:
            DataFrame with results
        """
        if frequency == 'monthly':
            return self.calculate_composite_index()
        else:
            raise ValueError("CI currently supports only monthly frequency")
