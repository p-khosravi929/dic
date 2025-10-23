import pandas as pd

def load_sample_data():
    """Load sample precipitation data"""
    return pd.DataFrame(columns=['year', 'month', 'precipitation'])

def export_to_excel(results_dict, filename='drought_indices_results.xlsx'):
    """
    Export multiple results to Excel file with different sheets
    
    Parameters:
    results_dict: dictionary of {sheet_name: DataFrame}
    filename: output filename
    """
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in results_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
