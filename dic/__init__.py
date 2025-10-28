"""
DIC - Drought Indices Calculation
A Python package for calculating various drought indices.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from dic.indices.czi import ChinaZIndex
from dic.indices.ci import CompositeIndex

__all__ = ['ChinaZIndex', 'CompositeIndex']
