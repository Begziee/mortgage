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



