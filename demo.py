"""
The file test the functionality of code.
"""

import sys
from pathlib import Path

from mortgage.calculator import MortgageCalculator

# Set up paths (only needed if running directly)
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


# Your existing code
mortgage = MortgageCalculator(
    loan_amount=330000, fixed_rate=4.5, tenure=30, fixed_tenure=30
)

print(mortgage.amortisation_schedule())
