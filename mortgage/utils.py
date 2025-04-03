import os
from functools import wraps
from datetime import datetime
import pandas as pd

def output_csv(func):
    """
    Decorator to save the output of a function to a CSV file.
    The CSV file will be named after the function with a timestamp.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Ensure output directory exists
        os.makedirs("output_files", exist_ok=True)

        # Get DataFrame from decorated function
        df = func(*args, **kwargs)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y_%m%d_%H%M%S")
        filename = f"{func.__name__}_{timestamp}.csv"
        filepath = os.path.join("output_files", filename)

        # Save DataFrame to CSV
        df.to_csv(filepath, index=False)
        print(f"Saved CSV to: {filepath}")
        return df
    return wrapper

def loan_summary_decorator(summary_func):
    """
    Decorator to enhance the loan summary with additional details.
    Includes overpayment details if applicable and comparison calculations if `compare` is True.
    """
    def wrapper(self, df: pd.DataFrame, loan_amount: float, overpayment_amount: float = 0, compare: bool = False):
        # Generate the base summary
        base_summary = summary_func(self, df, loan_amount, overpayment_amount)

        # Dynamically retrieve overpayment_amount if applicable
        overpayment_amount = getattr(self, "overpayment_amount", None)
        if overpayment_amount is None and "Payment overpayment" in df.columns:
            overpayment_amount = df["Payment overpayment"].iloc[0]

        # Add comparison details if `compare` is True
        if compare:
            total_paid_ratio_overpayment = round(df["Paid to date overpayment"].dropna().iloc[-1] / loan_amount, 2)
            total_years = df["Payment overpayment"].count() // 12
            total_months = df["Payment overpayment"].count() % 12
            interest_savings = round(
                df["Interest charged to date standard"].iloc[-1] -
                df["Interest charged to date overpayment"].dropna().iloc[-1],
                2
            )
            base_summary.append(
                f"💸 Comparison Summary:"
                f"\n   - Overpayment Repayment: £{total_paid_ratio_overpayment} per £1 borrowed"
                f"\n   - Mortgage Term with Overpayment: {total_years} year(s) and {total_months} month(s)"
                f"\n   - Interest Savings: £{interest_savings:,.2f}"
            )

        # Print the summary
        print("\n".join(base_summary))
        return base_summary

    return wrapper

