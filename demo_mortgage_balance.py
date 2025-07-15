"""
demo_mortgage_balance.py

This script demonstrates how to use the MortgageBalance class to generate
and display a mortgage balance. It creates a MortgageBalance
instance with sample parameters (loan amount, fixed rate, start date, payment history),
calculates the full payment schedule, and prints the resulting DataFrame.

Usage:
    python demo_mortgage_balance.py 

The output shows a detailed breakdown of mortgage daily balance as impacted by any repayment
"""

import sys
from pathlib import Path

from mortgage.calculator import MortgageBalance

# Set up paths (only needed if running directly)
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


mortgage = MortgageBalance(
    loan_amount=331794,
    fixed_rate=4.55,
    start_date="15/11/2024",
    payment_link="payment_schedule.csv",  # Update with your actual path
    daily_balance=True,
)

print(mortgage.calculate_balance())
