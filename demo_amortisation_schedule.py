"""
demo_amortisation_schedule.py

This script demonstrates how to use the MortgageCalculator class to generate
and display a mortgage amortisation schedule. It creates a MortgageCalculator
instance with sample parameters (loan amount, fixed rate, fixed tenure, and total tenure),
calculates the full payment schedule, and prints the resulting DataFrame.

Usage:
    python demo_amortisation_schedule.py

The output shows a detailed breakdown of monthly payments, interest, principal repaid,
and remaining loan balance over the life of the mortgage.
"""

from mortgage.calculator import MortgageCalculator

mc = MortgageCalculator(
    loan_amount=300000,
    fixed_rate=3.5,
    # variable_rate=6.5,
    fixed_tenure=5,
    tenure=30,
)

df = mc.amortisation_schedule()
print(df)
