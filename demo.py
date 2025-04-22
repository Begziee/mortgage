"""
The file test the functionality of code.
"""

import sys
from pathlib import Path

from mortgage.calculator import OverpaymentCalculator

# Set up paths (only needed if running directly)
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


# Your existing code
mortgage = OverpaymentCalculator(
    loan_amount=250000,
    fixed_rate=5.25,
    tenure=20,
    fixed_tenure=5,
    variable_rate=6.26,
    overpayment_amount=200,
    compare=True,
)

print(mortgage.overpayment_schedule())
