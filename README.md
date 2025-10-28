# DIC - Drought Indices Calculation

A comprehensive Python package for calculating various drought indices including China Z-Index (CZI), SPI, SPEI, and more.

## Features
- **China Z-Index (CZI)** - Wilson-Hilferty cube root transformation
- **Modified China Z-Index (MCZI)** - Uses median instead of mean for robust performance
- **Composite Index (CI)** - Combines SPI and moisture index components
- Multiple temporal scales (Monthly, Seasonal, Annual)
- Drought classification according to standard categories
- Easy-to-use API
- Export results to Excel/CSV

## Installation
```bash
git clone https://github.com/p-khosravi929/DIC.git
cd DIC
pip install -e .

Quick Start
python
from dic.indices.czi import ChinaZIndex
import pandas as pd

# Load your data
data = pd.read_csv('data.csv')

# Calculate CZI
calculator = ChinaZIndex(data)
monthly_results = calculator.calculate_monthly_czi()

## Available Indices
- China Z-Index (CZI)
- Modified China Z-Index (MCZI)
- Composite Index (CI)
- Standardized Precipitation Index (SPI)
- Standardized Precipitation Evapotranspiration Index (SPEI)
- Palmer Drought Severity Index (PDSI)
- Reconnaissance Drought Index (RDI)

## Modified CZI Usage

The Modified China Z-Index (MCZI) uses median instead of mean for better performance with skewed precipitation data:

```python
from dic.indices.mczi import ModifiedChinaZIndex
from dic.indices.czi import ChinaZIndex
import pandas as pd

# Load your data
data = pd.read_csv('data.csv')

# Calculate Modified CZI
mczi_calculator = ModifiedChinaZIndex(data)
czi_calculator = ChinaZIndex(data)

# Calculate both indices
mczi_results = mczi_calculator.calculate_monthly_mczi()
czi_results = czi_calculator.calculate_monthly_czi()

# Compare results
comparison = mczi_calculator.compare_with_czi(czi_calculator)

## **Key Features of MCZI Implementation:**
1. **Median-Based Calculation**: Uses median instead of mean as mentioned in the PDF
2. **Comparison Function**: Built-in method to compare MCZI with standard CZI
3. **Multiple Time Scales**: Monthly, seasonal, and annual calculations
4. **Robust Statistics**: Less sensitive to extreme precipitation values
5. **Comprehensive Testing**: Unit tests covering all functionality

## Composite Index Usage
The Composite Index (CI) combines short-term and medium-term SPI with moisture conditions:
```python
from dic.indices.ci import CompositeIndex
import pandas as pd

# Load your data
data = pd.read_csv('data.csv')

# Calculate Composite Index
calculator = CompositeIndex(data)
results = calculator.calculate_composite_index()

# View results
print(results[['year', 'month', 'Composite_Index', 'Drought_Class']].head())

Formula:
CI = 0.47 × SPI₁ + 0.36 × SPI₃ + 0.96 × M₃₀
Where:
SPI₁ = 1-month SPI
SPI₃ = 3-month SPI
M₃₀ = Monthly moisture index = (P - PE) / P

Documentation
See examples for usage examples.

Contributing
Contributions are welcome! Please feel free to submit pull requests.

License
No License
