"""
Example usage of Composite Index calculation
"""

import pandas as pd
import numpy as np
from dic.indices.ci import CompositeIndex

def main():
    # Load your data (replace with your actual data path)
    try:
        data = pd.read_csv('data/Monthly.csv')
        print("Loaded data from Monthly.csv")
    except FileNotFoundError:
        print("Sample data not found. Using generated sample data.")
        # Generate sample data for demonstration
        dates = pd.date_range('1987-01-01', '2017-12-31', freq='M')
        data = pd.DataFrame({
            'year': dates.year,
            'month': dates.month,
            'precipitation': np.random.gamma(2, 2, len(dates))
        })

    # Initialize Composite Index calculator
    calculator = CompositeIndex(data)
    
    # Calculate Composite Index
    results = calculator.calculate_composite_index()
    
    # Display results
    print("\n=== Composite Index Results ===")
    print(f"Total records: {len(results)}")
    print(f"Date range: {results['year'].min()}-{results['month'].min()} to {results['year'].max()}-{results['month'].max()}")
    
    # Display drought statistics
    drought_stats = results['Drought_Class'].value_counts()
    print("\nDrought Classification Statistics:")
    for category, count in drought_stats.items():
        percentage = (count / len(results)) * 100
        print(f"{category}: {count} months ({percentage:.1f}%)")
    
    # Identify severe drought periods
    severe_droughts = results[results['Drought_Class'].isin(['Severe Drought', 'Extreme Drought'])]
    print(f"\nSevere/Extreme Drought Months: {len(severe_droughts)}")
    
    if len(severe_droughts) > 0:
        print("Severe drought periods:")
        for _, row in severe_droughts.head(10).iterrows():
            print(f"  {int(row['year'])}-{int(row['month']):02d}: CI={row['Composite_Index']:.2f} ({row['Drought_Class']})")
    
    # Save results
    results.to_csv('composite_index_results.csv', index=False)
    print(f"\nResults saved to 'composite_index_results.csv'")
    
    # Save detailed results to Excel
    with pd.ExcelWriter('composite_index_detailed.xlsx') as writer:
        results.to_excel(writer, sheet_name='Composite_Index', index=False)
        
        # Add summary statistics
        summary = pd.DataFrame({
            'Statistic': ['Mean CI', 'Min CI', 'Max CI', 'Std CI', 
                         'Normal Months', 'Drought Months', 'Severe+ Drought Months'],
            'Value': [results['Composite_Index'].mean(), 
                     results['Composite_Index'].min(),
                     results['Composite_Index'].max(),
                     results['Composite_Index'].std(),
                     len(results[results['Drought_Class'] == 'Normal']),
                     len(results[results['Drought_Class'].str.contains('Drought')]),
                     len(severe_droughts)]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print("Detailed results saved to 'composite_index_detailed.xlsx'")

if __name__ == "__main__":
    main()
