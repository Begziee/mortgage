"""
helpers.py
Helper functions for the mortgage application.
This module contains utility functions for calculating
mortgage payments, cleaning data, and generating summaries.
It includes functions for fixed and variable rate payments,
cleaning DataFrame columns, and generating mortgage summaries.
"""

from typing import Union
from decimal import Decimal
from functools import lru_cache
import re

import pandas as pd


@lru_cache()
def _fixed_rate_payment(self) -> list[dict[str, Union[float, Decimal]]]:
    """
    Calculate the fixed monthly rate and payment amount for the loan amount
    based on the fixed interest rate and tenure

    Uses instance attributes:
        - fixed_rate (float): Fixed interest rate (float)
        - total_month (int): Loan tenure in months (int)
        - loan_amount (float): Amount borrowed (float)

    Returns:
        - fixed_rate_payment (list): List of dictionaries containing
        monthly rate and payment amount for the fixed rate
    """
    fixed_rate_payment = []
    monthly_rate = self.fixed_rate / (12 * 100)
    compounding_factor = (1 + monthly_rate) ** self.total_month
    payment = (
        self.loan_amount * monthly_rate * compounding_factor / (compounding_factor - 1)
    )

    fixed_rate_payment.append({"monthly_rate": monthly_rate, "payment": payment})
    return fixed_rate_payment


@lru_cache()
def _variable_rate_payment(
    self, current_balance: float
) -> list[dict[str, Union[float, Decimal]]]:
    """
    Calculate the variable monthly rate and payment amount for the loan amount
    based on the variable interest rate and tenure.

    Args:
        current_balance (float): Remaining loan principal (float)
    Uses instance attributes:
        - variable_rate (float): Variable interest rate (float)
        - tenure (int): Loan tenure in years (int)
        - fixed_tenure (int): Fixed tenure in years (int)
    Returns:
        - variable_rate_payment (list): List of dictionaries containing
        monthly rate and payment amount for the variable rate
    """
    variable_rate_payment = []
    monthly_rate = self.variable_rate / (12 * 100)
    total_month = (self.tenure - self.fixed_tenure) * 12
    compounding_factor = (1 + monthly_rate) ** total_month
    payment = (
        current_balance * monthly_rate * compounding_factor / (compounding_factor - 1)
    )

    variable_rate_payment.append({"monthly_rate": monthly_rate, "payment": payment})
    return variable_rate_payment


def _clean_and_convert_column(data_frame: pd.DataFrame, column_name: str) -> pd.Series:
    """
    Helper function to clean and convert a column to float by removing commas.

    Args:
        data_frame (pd.DataFrame): The DataFrame containing the column.
        column_name (str): The name of the column to clean and convert.

    Returns:
        pd.Series: The cleaned and converted column as a float series.
    """

    if (
        not data_frame[column_name].dtype == "object"
    ):  # Check if the column is not already strings
        data_frame[column_name] = data_frame[column_name].astype(
            str
        )  # Convert to strings
    return data_frame[column_name].str.replace(",", "").astype(float)


def _mortgage_summary(
    self, data_frame: pd.DataFrame, compare: bool = False
) -> list[str]:
    """
    Generator to dynamically create a loan summary.
    Includes overpayment details if applicable and
    comparison calculations if `compare` is True.

    Args:
        self: The instance of the class (MortgageCalculator or OverpaymentCalculator).
        data_frame (pd.DataFrame): The DataFrame containing loan details.
        loan_amount (float): The original loan amount.
        compare (bool): Whether to include comparison details.

    Returns:
        list[str]: A list of strings representing the loan summary.
    """
    # Base loan info
    output = [
        " Loan Summary",
        f"{'-'*30}",
        f"• Amount: £{self.loan_amount:,.2f}",
        f"• Term: {self.tenure} years ({self.total_month} months)",
    ]

    # Rate structure
    if self.fixed_tenure > 0:
        output.append(f"• Fixed: {self.fixed_rate:.2f}% for {self.fixed_tenure} years")
        if self.variable_rate:
            output.append(f"• Variable: {self.variable_rate:.2f}% thereafter")
    else:
        output.append(f"• Fixed Rate: {self.fixed_rate:.2f}% (full term)")

    # Dynamically retrieve overpayment_amount if applicable
    overpayment_amount = getattr(self, "overpayment_amount", None)
    if overpayment_amount is None and "Payment overpayment" in data_frame.columns:
        overpayment_amount = data_frame["Payment overpayment"].iloc[0]

    # Add overpayment details if applicable
    if overpayment_amount and overpayment_amount > 0:
        output.append(f"• Monthly Overpayment: £{overpayment_amount:,.2f}")

    # Handle "Repayment Ratio" based on the context
    if compare:
        # Use standard_ratio if compare is True
        standard_ratio = round(
            data_frame["Paid to date standard"].dropna().iloc[-1] / self.loan_amount, 2
        )
        output.append(f"• Repayment Ratio: £{standard_ratio} for every £1 borrowed")

        # Add comparison details
        overpayment_ratio = round(
            data_frame["Paid to date overpayment"].dropna().iloc[-1] / self.loan_amount,
            2,
        )
        total_years = data_frame["Payment overpayment"].count() // 12
        total_months = data_frame["Payment overpayment"].count() % 12
        # Calculate interest savings
        standard_interest = data_frame["Interest charged to date standard"].iloc[-1]
        overpyament_interest = (
            data_frame["Interest charged to date overpayment"].dropna().iloc[-1]
        )
        interest_savings = round(standard_interest - overpyament_interest, 2)

        # Append comparison details to output
        output.append(
            f" Comparison Summary:"
            f"\n - Overpayment Repayment Ratio: £{overpayment_ratio} per £1 borrowed"
            f"\n - Mortgage Term with Overpayment: {total_years} year(s) and {total_months} month(s)"
            f"\n - Interest Savings: £{interest_savings:,.2f}"
        )
    else:
        # Use paid_ratio if compare is False
        paid_ratio = round(
            data_frame["Paid to date"].dropna().iloc[-1] / self.loan_amount, 2
        )
        output.append(f"• Repayment Ratio: £{paid_ratio} for every £1 borrowed")
    return output


def _clean_currency(value):
    """Remove currency symbols and thousands separators, return float
    Args:
        value (str or float): The value to clean, can be a
                string with currency symbols or a float.
    Returns:
        float: The cleaned value as a float.
    """
    if isinstance(value, str):
        return float(re.sub(r"[^\d.]", "", value))
    return float(value)


def _append_payment_balance_schedule(
    schedule,
    date,
    opening_balance,
    days_since_last_payment,
    amount,
    rate,
    interest_accrued,
    principal_repaid,
    closing_balance,
):
    """
    Append a payment balance schedule entry.
    Args:
        schedule (list): The list to append the entry to.
        date (str): The date of the payment.
        opening_balance (float): The opening balance before the payment.
        days_since_last_payment (int): Number of days since the last payment.
        amount (float): The total payment amount.
        rate (float): The interest rate for the period.
        interest_accrued (float): Interest accrued during the period.
        principal_repaid (float): Principal repaid during the period.
        closing_balance (float): The closing balance after the payment.
    """
    schedule.append(
        {
            "Date": date,
            "Total Loan Balance B/F": f"£{opening_balance:,.2f}",
            "Number of days since last payment": days_since_last_payment,
            "Rate": rate,
            "Transaction": f"£{amount:,.2f}",
            "Mortgage Interest": f"£{interest_accrued:,.2f}",
            "Principal repaid": f"£{principal_repaid:,.2f}",
            "Total Loan Balance C/F": f"£{closing_balance:,.2f}",
        }
    )


def _append_schedule(
    payment_schedule,
    month,
    fixed_rate,
    payment,
    interest_payment,
    principal_payment,
    total_payment,
    total_interest_payment,
    total_principal_payment,
    loan_balance,
    equity,
):
    """
    Append a payment schedule entry with detailed information.
    Args:
        payment_schedule (list): The list to append the entry to.
        month (int): The month number in the payment schedule.
        fixed_rate (float): The fixed interest rate for the period.
        payment (float): The total payment amount for the period.
        interest_payment (float): Interest charged for the period.
        principal_payment (float): Principal repaid during the period.
        total_payment (float): Total payment made to date.
        total_interest_payment (float): Total interest charged to date.
        total_principal_payment (float): Total principal repaid to date.
        loan_balance (float): Remaining loan balance after the payment.
        equity (float): Equity percentage in the property.
    """

    payment_schedule.append(
        {
            "Month": month,
            "Rate": fixed_rate,
            "Rate type": "Fixed",
            "Payment": f"{payment:,.2f}",
            "Interest charged": f"{interest_payment:,.2f}",
            "Principal repaid ": f"{principal_payment:,.2f}",
            "Paid to date": f"{total_payment:,.2f}",
            "Interest charged to date": f"{total_interest_payment:,.2f}",
            "Principal repaid to date": f"{total_principal_payment:,.2f}",
            "Loan balance": f"{max(loan_balance, 0):,.2f}",
            "Equity": f"{equity:.2%}",
        }
    )
