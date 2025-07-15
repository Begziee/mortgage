"""
demo_overpayment_schedule.py

This script demonstrates how to use the OverpaymentCalculator class to generate
and display a mortgage amortisation schedule taking into account mothly overpayment. It creates a OverpaymentCalculator
instance with sample parameters (loan amount, fixed rate, fixed tenure,overpayment amount, and total tenure),
calculates the full payment schedule, and prints the resulting DataFrame.

Usage:
    python demo_overpayment_schedule.py

The output shows a detailed breakdown and comparison of the effect of monthly overpayment. 
"""

from mortgage.calculator import OverpaymentCalculator

mc = OverpaymentCalculator(
    loan_amount=300000,
    fixed_rate=3.5,
    # variable_rate=6.5,
    # fixed_tenure=5,
    compare=True,
    overpayment_amount=100,
    tenure=30,
)

df = mc.overpayment_schedule()
print(df.head())
