# DIC - Drought Indices Calculation

A comprehensive Python package for calculating various drought indices including China Z-Index (CZI), SPI, SPEI, and more.

## Features

- **China Z-Index (CZI)** - Wilson-Hilferty cube root transformation
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
Available Indices
China Z-Index (CZI)

Standardized Precipitation Index (SPI)

Standardized Precipitation Evapotranspiration Index (SPEI)

Palmer Drought Severity Index (PDSI)

Reconnaissance Drought Index (RDI)

Documentation
See examples for usage examples.

Contributing
Contributions are welcome! Please feel free to submit pull requests.

License
No License
