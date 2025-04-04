from functools import lru_cache
from typing import Union
from decimal import Decimal
import pandas as pd
from mortgage.utils import output_csv
from mortgage.helpers import _mortgage_summary, _clean_and_convert_column

class MortgageCalculator:
    """
    A class to calculate mortgage schedules for fixed and variable rate loans.
    """
    def __init__(self,
                 loan_amount,
                 fixed_rate,
                 tenure,
                 variable_rate=0,
                 fixed_tenure=0):
        self.loan_amount = loan_amount
        self.fixed_rate = fixed_rate
        self.variable_rate = variable_rate
        self.fixed_tenure = fixed_tenure
        self.tenure = tenure
        self.total_month = self.tenure * 12

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
        compounding_factor = (1 + monthly_rate)**self.total_month
        payment = (self.loan_amount * monthly_rate * compounding_factor /
                   (compounding_factor - 1))

        fixed_rate_payment.append({
            "monthly_rate": monthly_rate,
            "payment": payment
        })
        return fixed_rate_payment

    @lru_cache()
    def _variable_rate_payment(
            self,
            current_balance: float) -> list[dict[str, Union[float, Decimal]]]:
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
        compounding_factor = (1 + monthly_rate)**total_month
        payment = (current_balance * monthly_rate * compounding_factor /
                   (compounding_factor - 1))

        variable_rate_payment.append({
            "monthly_rate": monthly_rate,
            "payment": payment
        })
        return variable_rate_payment

    @lru_cache()
    def _fixed_payment_calculation(
            self) -> list[dict[str, Union[float, Decimal]]]:
        """
        Calculate the fixed payment schedule for the loan amount
        based on the fixed interest rate and tenure.

        Uses instance attributes:
            - loan_amount (float): Amount borrowed (float)
            - total_month (int): Loan tenure in months (int)
            - fixed_tenure (int): Fixed tenure in years (int)
        Returns:
            - payment_schedule (list): List of dictionaries containing
              payment schedule details for the fixed rate
        """
        # Initialise variables
        loan_balance = self.loan_amount
        payment_schedule = []
        total_payment = total_interest_payment = total_principal_payment = 0

        # Get fixed rate payment details
        fixed_rate_info = self._fixed_rate_payment()[0]
        monthly_rate = fixed_rate_info["monthly_rate"]
        payment = fixed_rate_info["payment"]

        for month in range(1, self.total_month + 1):
            # Calculate interest, principal, and remaining balance
            interest_payment = loan_balance * monthly_rate
            principal_payment = payment - interest_payment
            loan_balance -= principal_payment

            # Accumulate totals
            total_payment += payment
            total_interest_payment += interest_payment
            total_principal_payment += principal_payment
            equity = total_principal_payment / self.loan_amount

            # Append to schedule
            payment_schedule.append({
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
            })
        return payment_schedule

    @lru_cache()
    def _variable_payment_calculation(
            self) -> list[dict[str, Union[float, Decimal]]]:
        """
        Calculate the variable payment schedule for the loan amount
        based on the fixed and variable interest rate, and tenure.

        Uses instance attributes:
            - loan_amount (float): Amount borrowed (float)
            - total_month (int): Loan tenure in months (int)
            - fixed_tenure (int): Fixed tenure in years (int)
        Returns:
            - payment_schedule (list): List of dictionaries containing
              payment schedule details for the fixed and variable rate
        """
        # Initialise variables
        payment_schedule = []
        total_payment = total_interest_payment = total_principal_payment = 0
        loan_balance = self.loan_amount
        month = 1
        fixed_tenure_month = self.fixed_tenure * 12
        variable_monthly_rate = variable_payment = None

        # Get fixed rate payment details
        fixed_rate_info = self._fixed_rate_payment()[0]
        fixed_monthly_rate = fixed_rate_info["monthly_rate"]
        fixed_payment = fixed_rate_info["payment"]

        # Loop through each month until the loan is paid off
        while loan_balance >= 0 and month <= self.total_month:
            if month <= fixed_tenure_month:
                monthly_rate = fixed_monthly_rate
                payment = fixed_payment
                rate_type = "Fixed"
                rate = self.fixed_rate
            else:
                if variable_monthly_rate is None or variable_payment is None:
                    variable_rate_info = self._variable_rate_payment(
                        loan_balance)[0]
                    variable_monthly_rate = variable_rate_info["monthly_rate"]
                    variable_payment = variable_rate_info["payment"]
                monthly_rate = variable_monthly_rate
                payment = variable_payment
                rate_type = "Variable"
                rate = self.variable_rate

            # Calculate interest, principal, and remaining balance
            interest_payment = loan_balance * monthly_rate
            principal_payment = payment - interest_payment
            loan_balance -= principal_payment

            # Accumulate totals
            total_payment += payment
            total_interest_payment += interest_payment
            total_principal_payment += principal_payment
            equity = total_principal_payment / self.loan_amount

            # Append to schedule
            payment_schedule.append({
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
            })
            month = month + 1
        return payment_schedule

    @output_csv
    def amortisation_schedule(self) -> pd.DataFrame:
        """
        Calculate the amortisation schedule for the loan amount
        based on the fixed and variable interest rate, and tenure.

        Uses instance attributes:
            - loan_amount (float): Amount borrowed (float)

        Returns:
            amortisation_df: DataFrame containing the amortisation schedule
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

        if self.variable_rate == 0:
            amortisation_schedule = self._fixed_payment_calculation()
        else:
            amortisation_schedule = self._variable_payment_calculation()

        amortisation_df = pd.DataFrame(amortisation_schedule)

        amortisation_df["Paid to date"] = _clean_and_convert_column(
            amortisation_df, "Paid to date")
        print(f'{"="*30}')
        summary = _mortgage_summary(self, amortisation_df)
        print("\n".join(summary))

        return amortisation_df
