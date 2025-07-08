"""
The file test the functionality of code.
"""

import sys
from pathlib import Path

from mortgage.calculator import MortgageBalance

# Set up paths (only needed if running directly)
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


# Your existing code
mortgage = MortgageBalance(
    loan_amount=331794,
    fixed_rate=4.55,
    start_date="15/11/2024",
    payment_link="/Users/aramide/Documents/selfdev/mortgage/payment_schedule.csv",
    daily_balance=True,
)

print(mortgage.calculate_balance())
