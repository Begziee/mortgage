import pandas as pd

def _clean_and_convert_column(df: pd.DataFrame, column_name: str) -> pd.Series:
    """
    Helper function to clean and convert a column to float by removing commas.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column_name (str): The name of the column to clean and convert.
    
    Returns:
        pd.Series: The cleaned and converted column as a float series.
    """

    if not df[column_name].dtype == 'object':  # Check if the column is not already strings
        df[column_name] = df[column_name].astype(str)  # Convert to strings
    return df[column_name].str.replace(",", "").astype(float)


def _mortgage_summary(self, df: pd.DataFrame, compare: bool = False) -> list[str]:
    """
    Generator to dynamically create a loan summary.
    Includes overpayment details if applicable and comparison calculations if `compare` is True.

    Args:
        self: The instance of the class (MortgageCalculator or OverpaymentCalculator).
        df (pd.DataFrame): The DataFrame containing loan details.
        loan_amount (float): The original loan amount.
        compare (bool): Whether to include comparison details.

    Returns:
        list[str]: A list of strings representing the loan summary.
    """
    # Base loan info
    output = [
        f" Loan Summary",
        f"{'-'*30}",
        f"• Amount: £{self.loan_amount:,.2f}",
        f"• Term: {self.tenure} years ({self.total_month} months)"
    ]

    # Rate structure
    if self.fixed_tenure > 0:
        output.append(
            f"• Fixed: {self.fixed_rate:.2f}% for {self.fixed_tenure} years"
        )
        if self.variable_rate:
            output.append(
                f"• Variable: {self.variable_rate:.2f}% thereafter"
            )
    else:
        output.append(f"• Fixed Rate: {self.fixed_rate:.2f}% (full term)")

    # Dynamically retrieve overpayment_amount if applicable
    overpayment_amount = getattr(self, "overpayment_amount", None)
    if overpayment_amount is None and "Payment overpayment" in df.columns:
        overpayment_amount = df["Payment overpayment"].iloc[0]

    # Add overpayment details if applicable
    if overpayment_amount and overpayment_amount > 0:
        output.append(f"• Monthly Overpayment: £{overpayment_amount:,.2f}")

     # Handle "Repayment Ratio" based on the context
    if compare:
        # Use standard_ratio if compare is True
        standard_ratio = round(df["Paid to date standard"].dropna().iloc[-1] / self.loan_amount, 2)
        output.append(
            f"• Repayment Ratio: £{standard_ratio} for every £1 borrowed"
        )

        # Add comparison details
        overpayment_ratio = round(df["Paid to date overpayment"].dropna().iloc[-1] / self.loan_amount, 2)
        total_years = df["Payment overpayment"].count() // 12
        total_months = df["Payment overpayment"].count() % 12
        interest_savings = round(
            df["Interest charged to date standard"].iloc[-1] -
            df["Interest charged to date overpayment"].dropna().iloc[-1],
            2
        )
        output.append(
            f" Comparison Summary:"
            f"\n   - Overpayment Repayment Ratio: £{overpayment_ratio} per £1 borrowed"
            f"\n   - Mortgage Term with Overpayment: {total_years} year(s) and {total_months} month(s)"
            f"\n   - Interest Savings: £{interest_savings:,.2f}"
        )
    else:
        # Use paid_ratio if compare is False
        paid_ratio = round(df["Paid to date"].dropna().iloc[-1] / self.loan_amount, 2)
        output.append(
            f"• Repayment Ratio: £{paid_ratio} for every £1 borrowed"
        )
    return output