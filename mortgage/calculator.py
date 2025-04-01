import pandas as pd

class MortgageCalculator:
    def __init__(
        self, loan_amount, fixed_rate, tenure, variable_rate=0, fixed_tenure=0
    ):
        self.loan_amount = loan_amount
        self.fixed_rate = fixed_rate
        self.variable_rate = variable_rate
        self.fixed_tenure = fixed_tenure
        self.tenure = tenure
        self.total_month = self.tenure * 12
    
    
    def _fixed_rate_payment(self):
        fixed_rate_payment = []
        monthly_rate = self.fixed_rate / (12 * 100)
        compounding_factor = (1 + monthly_rate) ** self.total_month
        payment = (
            self.loan_amount
            * monthly_rate
            * compounding_factor
            / (compounding_factor - 1)
        )

        fixed_rate_payment.append({"monthly_rate": monthly_rate, "payment": payment})
        return fixed_rate_payment
    
    def _variable_rate_payment(self, current_balance):
        variable_rate_payment = []
        monthly_rate = self.variable_rate / (12 * 100)
        total_month = (self.tenure - self.fixed_tenure) * 12
        compounding_factor = (1 + monthly_rate) ** total_month
        payment = (
            current_balance
            * monthly_rate
            * compounding_factor
            / (compounding_factor - 1)
        )
        
        variable_rate_payment.append({"monthly_rate": monthly_rate, "payment": payment})
        return variable_rate_payment
    
    def _fixed_payment_calculation(self):
        loan_balance = self.loan_amount
        fixed_payment_schedule = []
        total_payment = total_interest_payment = total_principal_payment = 0

        fixed_rate_info = self._fixed_rate_payment()[0]
        monthly_rate = fixed_rate_info["monthly_rate"]
        payment = fixed_rate_info["payment"]

        for month in range(1, self.total_month + 1):
            interest_payment = loan_balance * monthly_rate
            principal_payment = payment - interest_payment

            loan_balance -= principal_payment
            total_payment += payment
            total_interest_payment += interest_payment
            total_principal_payment += principal_payment
            equity = total_principal_payment / self.loan_amount

            fixed_payment_schedule.append(
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
        return fixed_payment_schedule


    def _variable_payment_calculation(self):

        fixed_payment_schedule = []
        total_payment = total_interest_payment = total_principal_payment = 0
        loan_balance = self.loan_amount
        month = 1
        fixed_tenure_month = self.fixed_tenure * 12

        fixed_rate_info = self._fixed_rate_payment()[0]
        fixed_monthly_rate = fixed_rate_info["monthly_rate"]
        fixed_payment = fixed_rate_info["payment"]

        variable_monthly_rate = variable_payment = None

        while loan_balance >= 0 and month <= self.total_month:
            if month <= fixed_tenure_month:
                monthly_rate = fixed_monthly_rate
                payment = fixed_payment
                rate_type = "Fixed"
                rate = self.fixed_rate
            else:
                if variable_monthly_rate is None or variable_payment is None:
                    variable_rate_info = self._variable_rate_payment(loan_balance)[0]
                    variable_monthly_rate = variable_rate_info["monthly_rate"]
                    variable_payment = variable_rate_info["payment"]
                monthly_rate = variable_monthly_rate
                payment = variable_payment
                rate_type = "Variable"
                rate = self.variable_rate
            interest_payment = loan_balance * monthly_rate
            principal_payment = payment - interest_payment

            loan_balance -= principal_payment
            total_payment += payment
            total_interest_payment += interest_payment
            total_principal_payment += principal_payment
            equity = total_principal_payment / self.loan_amount


            fixed_payment_schedule.append(
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
            month = month + 1
        return fixed_payment_schedule
  
    def amortisation_schedule(self):

        if self.variable_rate == 0:
            amortisation_schedule = self._fixed_payment_calculation()
        else:
            amortisation_schedule = self._variable_payment_calculation()

        amortisation_df = pd.DataFrame(amortisation_schedule)
        amortisation_df["Paid to date"] = (
            amortisation_df["Paid to date"].str.replace(",", "").astype(float)
        )
        print("____________________________________")
        print(
            f'This means you will pay back £{round(amortisation_df["Paid to date"].iloc[-1]/self.loan_amount,2)} for every £1 borrowed.'
        )
        return amortisation_df