"""
Example usage of China Z-Index calculation
"""

import pandas as pd
from dic.indices.czi import ChinaZIndex

def main():
    # Load your data (replace with your actual data path)
    try:
        data = pd.read_csv('data/Monthly.csv')
    except FileNotFoundError:
        print("Sample data not found. Using generated sample data.")
        # Generate sample data for demonstration
        import numpy as np
        dates = pd.date_range('1987-01-01', '2017-12-31', freq='M')
        data = pd.DataFrame({
            'year': dates.year,
            'month': dates.month,
            'precipitation': np.random.gamma(2, 2, len(dates))
        })
    
    # Initialize CZI calculator
    calculator = ChinaZIndex(data)
    
    # Calculate at different frequencies
    monthly_results = calculator.calculate_monthly_czi()
    seasonal_results = calculator.calculate_seasonal_czi()
    annual_results = calculator.calculate_annual_czi()
    
    # Save results
    with pd.ExcelWriter('czi_results.xlsx') as writer:
        monthly_results.to_excel(writer, sheet_name='Monthly', index=False)
        seasonal_results.to_excel(writer, sheet_name='Seasonal', index=False)
        annual_results.to_excel(writer, sheet_name='Annual', index=False)
    
    print("CZI calculation completed!")
    print(f"Monthly results: {len(monthly_results)} records")
    print(f"Seasonal results: {len(seasonal_results)} records")
    print(f"Annual results: {len(annual_results)} records")
    print("Results saved to 'czi_results.xlsx'")

if __name__ == "__main__":
    main()
