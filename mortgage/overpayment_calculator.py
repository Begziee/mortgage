"""
This module contains the OverpaymentCalculator class, which extends the MortgageCalculator
to calculate overpayment schedules for fixed and variable rate mortgages.
"""

from functools import lru_cache
from typing import Union, List, Dict
from decimal import Decimal

import pandas as pd

from .utils import output_csv
from .helpers import _mortgage_summary, _clean_and_convert_column
from .calculator import MortgageCalculator


class OverpaymentCalculator(MortgageCalculator):
    """
    A class to calculate overpayment schedules for fixed and variable rate mortgages.
    Inherits from MortgageCalculator.
    """
    def _fixed_overpayment_calculation(
        self, overpayment_amount
    ) -> list[dict[str, Union[float, Decimal]]]:
        """
        Calculate the fixed overpayment schedule for the loan amount
        based on the fixed interest rate, tenure and overpayment amount.

        Args:
            overpayment_amount (float): Amount to overpay each month (float)

        Uses instance attributes:
            - loan_amount (float): Amount borrowed (float)
            - fixed_rate (float): Fixed interest rate (float)
        Returns:
            - overpayment_schedule (list): List of dictionaries containing
              payment schedule details for the overpayment amount.
        """
        # Initialise variables
        loan_balance = self.loan_amount
        overpayment_schedule = []
        total_payment = total_interest_payment = total_principal_payment = 0
        month = 1

        # Precompute fixed rate details
        fixed_rate_info = self._fixed_rate_payment()[0]
        fixed_monthly_rate = fixed_rate_info["monthly_rate"]
        fixed_payment = fixed_rate_info["payment"]

        while loan_balance > 1e-2:
            interest_payment = loan_balance * fixed_monthly_rate
            # Handle the final payment to avoid overpaying
            payment = round(
                min(
                    loan_balance + interest_payment,
                    fixed_payment + overpayment_amount,
                ),
                2,
            )
            principal_payment = payment - interest_payment

            # Calculate remaining balance
            loan_balance -= principal_payment

            # Accumulate totals
            total_payment += payment
            total_interest_payment += interest_payment
            total_principal_payment += principal_payment
            equity = total_principal_payment / self.loan_amount

            # Append to schedule
            overpayment_schedule.append(
                {
                    "Month": month,
                    "Rate": self.fixed_rate,
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
            month += 1
            if loan_balance <= 1e-2:
                break
        return overpayment_schedule

    def _variable_overpayment_calculation(
        self, overpayment_amount
    ) -> list[dict[str, Union[float, Decimal]]]:
        """
        Calculate the variable overpayment schedule for the loan amount
        based on the variable interest rate, tenure and overpayment amount.

        Args:
            overpayment_amount (float): Amount to overpay each month (float)

        Uses instance attributes:
            - loan_amount (float): Amount borrowed (float)
            - fixed_rate (float): Fixed interest rate (float)
            - variable_rate (float): Variable interest rate (float)
            - fixed_tenure (int): Fixed tenure in years (int)

        Returns:
            overpayment_df: DataFrame containing the amortisation schedule
                - 'Month' (int): Month number
                - 'Rate' (float): Applicable interest rate
                - 'Rate type' (str): Type of interest rate (Fixed/Variable)
                - 'Payment' (float): Monthly payment amount
                - 'Interest charged' (float): Interest charged for the month
                - 'Principal repaid' (float): Principal repaid for the month
                - 'Paid to date' (float): Total amount paid to date
                - 'Interest charged to date' (float): Total interest charged to date
                - 'Principal repaid to date' (float): Total principal repaid to date
                - 'Loan balance' (float): Remaining loan balance
                - 'Equity' (float): Equity percentage
        """

        # Initialise variables
        overpayment_schedule = []
        total_payment = total_interest_payment = total_principal_payment = 0
        variable_monthly_rate = variable_payment = None
        loan_balance = self.loan_amount
        fixed_tenure_month = self.fixed_tenure * 12
        month = 1

        # Precompute fixed rate details
        fixed_rate_info = self._fixed_rate_payment()[0]
        fixed_monthly_rate = fixed_rate_info["monthly_rate"]
        fixed_payment = fixed_rate_info["payment"]

        while loan_balance > 1e-2:
            if month <= fixed_tenure_month:
                monthly_rate = fixed_monthly_rate
                rate_type = "Fixed"
                rate = self.fixed_rate
                fixed_interest_payment = loan_balance * monthly_rate
                # Handle the final payment to avoid overpaying
                payment = round(
                    min(
                        loan_balance + fixed_interest_payment,
                        fixed_payment + overpayment_amount,
                    ),
                    2,
                )
            else:
                if variable_monthly_rate is None or variable_payment is None:
                    variable_rate_info = self._variable_rate_payment(loan_balance)[0]
                    variable_monthly_rate = variable_rate_info["monthly_rate"]
                    variable_payment = variable_rate_info["payment"]
                monthly_rate = variable_monthly_rate
                rate_type = "Variable"
                rate = self.variable_rate
                variable_interest_payment = loan_balance * monthly_rate
                # Handle the final payment to avoid overpaying
                payment = round(
                    min(
                        loan_balance + variable_interest_payment,
                        variable_payment + overpayment_amount,
                    ),
                    2,
                )

            # Calculate interest and principal payments and remaining balance
            interest_payment = loan_balance * monthly_rate
            principal_payment = payment - interest_payment
            loan_balance -= principal_payment

            # Accumulate total
            total_payment += payment
            total_interest_payment += interest_payment
            total_principal_payment += principal_payment
            equity = total_principal_payment / self.loan_amount

            # Append to schedule
            overpayment_schedule.append(
                {
                    "Month": month,
                    "Rate": rate,
                    "Rate type": rate_type,
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
            month += 1
            # Check if the loan is paid off
            if loan_balance <= 1e-2:
                break
        return overpayment_schedule

    @output_csv
    def overpayment_schedule(self, overpayment_amount, compare=False) -> pd.DataFrame:
        """
        Calculate the overpayment schedule for the loan amount
        based on the fixed or variable interest rate, tenure and overpayment amount.
        Args:
            overpayment_amount (float): Amount to overpay each month (float)
            compare (bool): Whether to compare with standard amortization schedule (default: False)
        Returns:
            - overpayment_df (pd.DataFrame): DataFrame containing the overpayment schedule.
                - 'Month' (int): Month number
                - 'Rate' (float): Applicable interest rate
                - 'Rate type' (str): Type of interest rate (Fixed/Variable)
                - 'Payment' (float): Monthly payment amount
                - 'Interest charged' (float): Interest charged for the month
                - 'Principal repaid' (float): Principal repaid for the month
                - 'Paid to date' (float): Total amount paid to date
                - 'Interest charged to date' (float): Total interest charged to date
                - 'Principal repaid to date' (float): Total principal repaid to date
                - 'Loan balance' (float): Remaining loan balance
                - 'Equity' (float): Equity percentage
        """
        self.overpayment_amount = overpayment_amount
        if self.variable_rate == 0:
            overpayment_schedule = self._fixed_overpayment_calculation(
                overpayment_amount
            )
        else:
            overpayment_schedule = self._variable_overpayment_calculation(
                overpayment_amount
            )

        overpayment_df = pd.DataFrame(overpayment_schedule)
        overpayment_df["Paid to date"] = _clean_and_convert_column(
            overpayment_df, "Paid to date"
        )
        if not compare:
            print(f'{"="*30}')
            summary = _mortgage_summary(self, overpayment_df)
            print("\n".join(summary))
            return overpayment_df
        
        amortization_df = self.amortisation_schedule()
        overpayment_df = pd.merge(
                amortization_df,
                overpayment_df,
                on="Month",
                how="left",
                suffixes=(" standard", " overpayment"),
            )
        overpayment_df["Paid to date overpayment"] = _clean_and_convert_column(
                overpayment_df, "Paid to date overpayment"
            )
        overpayment_df["Interest charged to date standard"] = (
                _clean_and_convert_column(
                    overpayment_df, "Interest charged to date standard"
                )
            )
        overpayment_df["Interest charged to date overpayment"] = (
                _clean_and_convert_column(
                    overpayment_df, "Interest charged to date overpayment"
                )
            )

        print(f'{"="*30}')
        summary = _mortgage_summary(self, overpayment_df, compare=True)
        print("\n".join(summary))
        return overpayment_df
