"""
Example usage of Modified China Z-Index calculation
and comparison with standard CZI
"""

import pandas as pd
import numpy as np
from dic.indices.mczi import ModifiedChinaZIndex
from dic.indices.czi import ChinaZIndex

def main():
    # Load your data (replace with your actual data path)
    try:
        data = pd.read_csv('data/Monthly.csv')
        print("Loaded data from Monthly.csv")
    except FileNotFoundError:
        print("Sample data not found. Using generated sample data.")
        # Generate sample data for demonstration
        dates = pd.date_range('1987-01-01', '2017-12-31', freq='M')
        np.random.seed(42)  # For reproducible results
        data = pd.DataFrame({
            'year': dates.year,
            'month': dates.month,
            'precipitation': np.random.gamma(2, 2, len(dates))
        })

    # Initialize both MCZI and CZI calculators
    mczi_calculator = ModifiedChinaZIndex(data)
    czi_calculator = ChinaZIndex(data)
    
    # Calculate MCZI at different frequencies
    monthly_results = mczi_calculator.calculate_monthly_mczi()
    seasonal_results = mczi_calculator.calculate_seasonal_mczi()
    annual_results = mczi_calculator.calculate_annual_mczi()
    
    # Compare MCZI with CZI
    comparison_results = mczi_calculator.compare_with_czi(czi_calculator)
    
    # Display results
    print("\n=== Modified CZI Results ===")
    print(f"Monthly records: {len(monthly_results)}")
    print(f"Seasonal records: {len(seasonal_results)}")
    print(f"Annual records: {len(annual_results)}")
    
    # Display drought statistics for MCZI
    mczi_drought_stats = monthly_results['Drought_Class'].value_counts()
    print("\nMCZI Drought Classification Statistics:")
    for category, count in mczi_drought_stats.items():
        percentage = (count / len(monthly_results)) * 100
        print(f"  {category}: {count} months ({percentage:.1f}%)")
    
    # Comparison statistics
    agreement_rate = comparison_results['Class_Agreement'].mean() * 100
    mean_difference = comparison_results['Difference'].mean()
    abs_mean_difference = comparison_results['Difference'].abs().mean()
    
    print(f"\n=== MCZI vs CZI Comparison ===")
    print(f"Classification agreement: {agreement_rate:.1f}%")
    print(f"Mean difference (MCZI - CZI): {mean_difference:.4f}")
    print(f"Absolute mean difference: {abs_mean_difference:.4f}")
    
    # Identify where differences occur
    disagreements = comparison_results[~comparison_results['Class_Agreement']]
    print(f"\nDisagreements in classification: {len(disagreements)} months")
    
    if len(disagreements) > 0:
        print("\nSample disagreements:")
        for _, row in disagreements.head(5).iterrows():
            print(f"  {int(row['year'])}-{int(row['month']):02d}: "
                  f"MCZI={row['MCZI']:.2f} ({row['Drought_Class']}) vs "
                  f"CZI={row['CZI']:.2f} ({row['CZI_Drought_Class']})")
    
    # Save results
    with pd.ExcelWriter('mczi_analysis_results.xlsx') as writer:
        monthly_results.to_excel(writer, sheet_name='MCZI_Monthly', index=False)
        seasonal_results.to_excel(writer, sheet_name='MCZI_Seasonal', index=False)
        annual_results.to_excel(writer, sheet_name='MCZI_Annual', index=False)
        comparison_results.to_excel(writer, sheet_name='MCZI_CZI_Comparison', index=False)
        
        # Add summary statistics
        summary_data = {
            'Statistic': [
                'Total Months', 'MCZI-CZI Agreement Rate', 
                'Mean Difference', 'Absolute Mean Difference',
                'MCZI Mean', 'CZI Mean', 'MCZI Std', 'CZI Std'
            ],
            'Value': [
                len(monthly_results),
                agreement_rate,
                mean_difference,
                abs_mean_difference,
                monthly_results['MCZI'].mean(),
                comparison_results['CZI'].mean(),
                monthly_results['MCZI'].std(),
                comparison_results['CZI'].std()
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\nResults saved to 'mczi_analysis_results.xlsx'")
    
    # Save individual CSV files
    monthly_results.to_csv('mczi_monthly_results.csv', index=False)
    comparison_results.to_csv('mczi_czi_comparison.csv', index=False)
    print("Individual CSV files saved")

def demonstrate_median_advantage():
    """
    Demonstrate the advantage of using median in skewed data
    """
    print("\n=== Demonstrating Median Advantage ===")
    
    # Create skewed precipitation data
    np.random.seed(42)
    skewed_data = np.random.gamma(1, 1, 1000)  # Highly skewed data
    skewed_data = np.append(skewed_data, [50, 60, 70])  # Add extreme values
    
    mean_val = np.mean(skewed_data)
    median_val = np.median(skewed_data)
    
    print(f"Skewed data statistics:")
    print(f"  Mean: {mean_val:.2f}")
    print(f"  Median: {median_val:.2f}")
    print(f"  Skewness: {stats.skew(skewed_data):.2f}")
    print(f"  Difference (Mean - Median): {mean_val - median_val:.2f}")
    print("\nThe median is less affected by extreme values, making MCZI more robust.")

if __name__ == "__main__":
    main()
    demonstrate_median_advantage()
