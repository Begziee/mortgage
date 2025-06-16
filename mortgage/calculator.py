"""
    Core program used to simulate the mortgage schedules. 
    Comprises of two classes MortgageCalculator and OverpaymentCalculator
"""

from functools import lru_cache
from typing import Union
from decimal import Decimal
from datetime import datetime
import pandas as pd
from mortgage.utils import output_csv
from mortgage.helpers import (
    _mortgage_summary,
    _clean_and_convert_column,
    _variable_rate_payment,
    _fixed_rate_payment,
    _clean_currency,
    _append_payment_balance_schedule,
    _append_schedule,
)


class MortgageCalculator:
    """
    A class to calculate mortgage schedules for fixed and variable rate loans.

    This class provides functionality to compute monthly mortgage payments,
    total interest paid, and remaining balances for both fixed and variable
    rate loans. It takes into account the loan amount, interest rates, and
    tenure to help users understand their mortgage obligations.
    """

    def __init__(
        self, loan_amount, fixed_rate, tenure, variable_rate=0, fixed_tenure=0
    ):
        self.loan_amount = loan_amount
        self.fixed_rate = fixed_rate
        self.variable_rate = variable_rate
        self.fixed_tenure = fixed_tenure
        self.tenure = tenure
        self.total_month = self.tenure * 12

    @lru_cache()
    def _fixed_payment_calculation(self) -> list[dict[str, Union[float, Decimal]]]:
        """
        Calculate the fixed payment schedule for the loan amount
        based on the fixed interest rate and tenure.

        Uses instance attributes:
            - loan_amount (float): Amount borrowed (float)
            - total_month (int): Loan tenure in months (int)
            - fixed_tenure (int): Fixed tenure in years (int)
            - fixed_rate (float): Fixed interest rate (float)
        Returns:
            - payment_schedule (list): List of dictionaries containing
              payment schedule details for the fixed rate
        """
        # Initialise variables
        loan_balance = self.loan_amount
        payment_schedule = []
        total_payment = total_interest_payment = total_principal_payment = 0

        # Get fixed rate payment details
        fixed_rate_info = _fixed_rate_payment(self)[0]
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
            _append_schedule(
                payment_schedule,
                month,
                self.fixed_rate,
                "Fixed",
                payment,
                interest_payment,
                principal_payment,
                total_payment,
                total_interest_payment,
                total_principal_payment,
                max(loan_balance, 0),
                equity,
            )

        return payment_schedule

    @lru_cache()
    def _variable_payment_calculation(self) -> list[dict[str, Union[float, Decimal]]]:
        """
        Calculate the variable payment schedule for the loan amount
        based on the fixed and variable interest rate, and tenure.

        Uses instance attributes:
            - loan_amount (float): Amount borrowed (float)
            - total_month (int): Loan tenure in months (int)
            - fixed_tenure (int): Fixed tenure in years (int)
            - fixed_rate (float): Fixed interest rate (float)
            - variable_rate (float): Variable interest rate (float)

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
        fixed_rate_info = _fixed_rate_payment(self)[0]
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
                    variable_rate_info = _variable_rate_payment(self, loan_balance)[0]
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

            _append_schedule(
                payment_schedule,
                month,
                rate,
                rate_type,
                payment,
                interest_payment,
                principal_payment,
                total_payment,
                total_interest_payment,
                total_principal_payment,
                max(loan_balance, 0),
                equity,
            )
            month = month + 1
        return payment_schedule

    @output_csv
    def amortisation_schedule(self) -> pd.DataFrame:
        """
        Calculate the amortisation schedule for the loan amount
        based on the fixed and variable interest rate, and tenure.

        Uses instance attributes:
            - variable_rate (float): Variable interest rate (float)

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
            amortisation_df, "Paid to date"
        )
        print(f'{"="*30}')
        summary = _mortgage_summary(self, amortisation_df)
        print("\n".join(summary))

        return amortisation_df


class OverpaymentCalculator(MortgageCalculator):
    """
    A class to calculate overpayment schedules for fixed and variable rate mortgages.
    Inherits from MortgageCalculator.
    """

    def __init__(
        self,
        loan_amount,
        fixed_rate,
        tenure,
        variable_rate=0,
        fixed_tenure=0,
        overpayment_amount=0,
        compare=False,
    ):
        super().__init__(loan_amount, fixed_rate, tenure, variable_rate, fixed_tenure)
        self.overpayment_amount = overpayment_amount
        self.compare = compare

    def _fixed_overpayment_calculation(self) -> list[dict[str, Union[float, Decimal]]]:
        """
        Calculate the fixed overpayment schedule for the loan amount
        based on the fixed interest rate, tenure and overpayment amount.

        Uses instance attributes:
            - overpayment_amount (float): Amount to overpay each month (float)
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
        fixed_rate_info = _fixed_rate_payment(self)[0]
        fixed_monthly_rate = fixed_rate_info["monthly_rate"]
        fixed_payment = fixed_rate_info["payment"]

        while loan_balance > 1e-2:
            interest_payment = loan_balance * fixed_monthly_rate
            # Handle the final payment to avoid overpaying
            payment = round(
                min(
                    loan_balance + interest_payment,
                    fixed_payment + self.overpayment_amount,
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
            _append_schedule(
                overpayment_schedule,
                month,
                self.fixed_rate,
                "Fixed",
                payment,
                interest_payment,
                principal_payment,
                total_payment,
                total_interest_payment,
                total_principal_payment,
                max(loan_balance, 0),
                equity,
            )
            month += 1
            if loan_balance <= 1e-2:
                break
        return overpayment_schedule

    def _variable_overpayment_calculation(
        self,
    ) -> list[dict[str, Union[float, Decimal]]]:
        """
        Calculate the variable overpayment schedule for the loan amount
        based on the variable interest rate, tenure and overpayment amount.

        Uses instance attributes:
            - overpayment_amount (float): Amount to overpay each month (float)
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
        fixed_rate_info = _fixed_rate_payment(self)[0]
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
                        fixed_payment + self.overpayment_amount,
                    ),
                    2,
                )
            else:
                if variable_monthly_rate is None or variable_payment is None:
                    variable_rate_info = _variable_rate_payment(self, loan_balance)[0]
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
                        variable_payment + self.overpayment_amount,
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
            _append_schedule(
                overpayment_schedule,
                month,
                rate,
                rate_type,
                payment,
                interest_payment,
                principal_payment,
                total_payment,
                total_interest_payment,
                total_principal_payment,
                max(loan_balance, 0),
                equity,
            )
            month += 1
            # Check if the loan is paid off
            if loan_balance <= 1e-2:
                break
        return overpayment_schedule

    @output_csv
    def overpayment_schedule(self) -> pd.DataFrame:
        """
        Calculate the overpayment schedule for the loan amount
        based on the fixed or variable interest rate, tenure and overpayment amount.

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
        #  self.overpayment_amount = overpayment_amount
        if self.variable_rate == 0:
            overpayment_schedule = self._fixed_overpayment_calculation()
        else:
            overpayment_schedule = self._variable_overpayment_calculation()

        overpayment_df = pd.DataFrame(overpayment_schedule)
        overpayment_df["Paid to date"] = _clean_and_convert_column(
            overpayment_df, "Paid to date"
        )
        if not self.compare:
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
        overpayment_df["Interest charged to date standard"] = _clean_and_convert_column(
            overpayment_df, "Interest charged to date standard"
        )
        overpayment_df[
            "Interest charged to date overpayment"
        ] = _clean_and_convert_column(
            overpayment_df, "Interest charged to date overpayment"
        )

        print(f'{"="*30}')
        summary = _mortgage_summary(self, overpayment_df, compare=True)
        print("\n".join(summary))
        return overpayment_df


class MortgageBalance(MortgageCalculator):
    """
    A class to calculate the mortgage balance for a given loan amount,
    fixed interest rate, start date, and payment schedule.
    Inherits from MortgageCalculator.
    """

    def __init__(
        self,
        loan_amount,
        fixed_rate,
        start_date,
        payment_link,
        tenure=0,
        fixed_tenure=0,
        variable_rate=0,
        daily_balance=False,
        today_payment=0,
    ):
        super().__init__(loan_amount, fixed_rate, tenure, variable_rate, fixed_tenure)
        self.start_date = start_date
        self.payment_link = payment_link
        self.repayment_amount = 0
        self.end_date = None
        self.daily_rate = self.fixed_rate / 36500
        self.daily_balance = daily_balance
        self.today_payment = today_payment

    # @output_csv
    def _daily_balance(self):
        """
        Calculate the mortgage balance based on the payment schedule.
        Uses instance attributes:
            - loan_amount (float): Amount borrowed (float)
            - fixed_rate (float): Fixed interest rate (float)
            - start_date (str): Start date of the mortgage in "dd/mm/yyyy" format
            - payment_link (str): Path to the CSV file containing payment schedule
            - today_payment (float): Payment amount for today
        Returns:
            - pd.DataFrame: DataFrame containing the mortgage balance schedule.
                - 'Date' (datetime): Date of the payment
                - 'Total Loan Balance B/F' (str): Opening balance before payment
                - 'Rate' (float): Interest rate
                - 'Transaction' (str): Payment amount
                - 'Mortgage Interest' (str): Interest accrued for the period
                - 'Principal repaid' (str): Principal repaid in the payment
                - 'Total Loan Balance C/F' (str): Closing balance after payment
        """

        current_balance = self.loan_amount
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        if self.end_date is None:
            self.end_date = today
        else:
            self.end_date = datetime.strptime(self.end_date, "%d/%m/%Y")

        # Generate a date range from the start date to the end date
        date_range = pd.date_range(self.start_date, self.end_date, freq="D")

        schedule = pd.DataFrame(
            index=date_range,
            columns=[
                "Date",
                "Total Loan Balance B/F",
                "Rate",
                "Transaction",
                "Mortgage Interest",
                "Principal repaid",
                "Total Loan Balance C/F",
            ],
        )

        # Read the payment schedule from the CSV file
        payments = pd.read_csv(
            self.payment_link, sep=",", header=0, names=["payment_date", "amount"]
        )
        payments["payment_date"] = pd.to_datetime(
            payments["payment_date"], dayfirst=True
        )

        # Calculate daily schedule
        for date in date_range:
            if date == today:
                payment = self.today_payment
            else:
                payment = payments.loc[payments["payment_date"] == date, "amount"].sum()
            daily_interest = current_balance * self.daily_rate
            closing_balance = current_balance + daily_interest - payment
            schedule.loc[date] = {
                "Date": date,
                "Total Loan Balance B/F": f"£{current_balance:,.2f}",
                "Rate": self.fixed_rate,
                "Transaction": f"£{payment:,.2f}",
                "Mortgage Interest": f"£{daily_interest:,.2f}",
                "Principal repaid": f"£{payment - daily_interest:,.2f}",
                "Total Loan Balance C/F": f"£{closing_balance:,.2f}",
            }
            # Update current balance for the next iteration
            current_balance = closing_balance
        # Reset index and format the date column
        schedule = schedule.reset_index().rename(columns={"index": "date"})
        schedule["date"] = pd.to_datetime(schedule["date"]).dt.date

        # Add additional columns for reporting
        schedule["Description"] = ""
        schedule.loc[
            schedule["Transaction"].apply(_clean_currency) > 0, "Description"
        ] = "Payment"

        # Reorder columns to match original format
        final_schedule = schedule[
            [
                "Date",
                "Total Loan Balance B/F",
                "Rate",
                "Transaction",
                "Description",
                "Mortgage Interest",
                "Principal repaid",
                "Total Loan Balance C/F",
            ]
        ]
        return pd.DataFrame(final_schedule)

    def _payment_day_balance(self):
        """
        This method reads the payment schedule from a CSV file and calculates
        the mortgage balance based on the payment dates and amounts.
        Uses instance attributes:
            - loan_amount (float): Amount borrowed (float)
            - fixed_rate (float): Fixed interest rate (float)
            - start_date (str): Start date of the mortgage in "dd/mm/yyyy" format
            - payment_link (str): Path to the CSV file containing payment schedule
            - today_payment (float): Payment amount for today
        Returns:
            - pd.DataFrame: DataFrame containing the mortgage balance schedule.
                - 'Date' (datetime): Date of the payment
                - 'Total Loan Balance B/F' (str): Opening balance before payment
                - 'Number of days since last payment' (int): Days since last payment
                - 'Rate' (float): Interest rate
                - 'Transaction' (str): Payment amount
                - 'Mortgage Interest' (str): Interest accrued for the period
                - 'Principal repaid' (str): Principal repaid in the payment
                - 'Total Loan Balance C/F' (str): Closing balance after payment
        """
        # Initialise variables
        opening_balance = closing_balance = self.loan_amount
        last_payment_date = datetime.strptime(self.start_date, "%d/%m/%Y")

        # Read the payment schedule from the CSV file
        payments = pd.read_csv(
            self.payment_link, sep=",", header=0, names=["payment_date", "amount"]
        )

        # Create a list to store the schedule
        schedule = []

        # Iterate through each payment in the schedule
        for _, column in payments.iterrows():
            opening_balance = closing_balance
            payment_date = datetime.strptime(str(column["payment_date"]), "%d/%m/%Y")
            days_since_last_payment = (payment_date - last_payment_date).days

            # Calculate interest accrued and principal repaid
            # interest_accrued = current_balance * self.daily_rate * days_since_last_payment
            interest_accrued = opening_balance * (
                (1 + self.daily_rate) ** days_since_last_payment - 1
            )
            principal_repaid = float(column["amount"]) - interest_accrued

            # Update current balance
            closing_balance -= principal_repaid

            # Append to schedule
            _append_payment_balance_schedule(
                schedule,
                payment_date,
                opening_balance,
                days_since_last_payment,
                column["amount"],
                self.fixed_rate,
                interest_accrued,
                principal_repaid,
                closing_balance,
            )
            last_payment_date = payment_date

        # Calculate today's balance
        opening_balance = closing_balance
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        days_since_last_payment = (today - last_payment_date).days
        interest_accrued = opening_balance * (
            (1 + self.daily_rate) ** days_since_last_payment - 1
        )
        principal_repaid = self.today_payment - interest_accrued
        closing_balance = opening_balance - principal_repaid

        # Append to schedule
        _append_payment_balance_schedule(
            schedule,
            today,
            opening_balance,
            days_since_last_payment,
            self.today_payment,
            self.fixed_rate,
            interest_accrued,
            principal_repaid,
            closing_balance,
        )
        # Convert the schedule to a DataFrame
        return pd.DataFrame(schedule)

    def calculate_balance(self):
        """
        Calculate the mortgage balance based on the payment schedule and conditions set.

        Uses instance attributes:
            - daily_balance (bool): If True, amortises the balance daily; otherwise, amortises using transaction date.
        Returns:
            - schedule_df (pd.DataFrame): DataFrame containing the mortgage balance schedule.
        """
        if self.daily_balance is True:
            schedule_df = self._daily_balance()
        else:
            schedule_df = self._payment_day_balance()
        print(schedule_df)
