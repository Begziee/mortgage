from mortgage.calculator import MortgageCalculator
from mortgage.overpayment_calculator import OverpaymentCalculator


if __name__ == "__main__":

    mortgage = MortgageCalculator(loan_amount=331794, fixed_rate=4.55, tenure=30)
    print(f'{"="*20} Fixed Mortgage Calculator {"="*20}')
    print(mortgage.amortisation_schedule())

    mortgage = MortgageCalculator(
        loan_amount=331794,
        fixed_rate=4.55,
        tenure=30,
        variable_rate=6.99,
        fixed_tenure=5,
    )
    print(f'{"="*20} Variable Mortgage Calculator {"="*20}')
    print(mortgage.amortisation_schedule())

    mortgage = OverpaymentCalculator(
        loan_amount=331794,
        fixed_rate=4.55,
        variable_rate=6.99,
        tenure=30,
        fixed_tenure=5,
    )
    print(f'{"="*20} Variable Mortgage Overpayment Calculator {"="*20}')
    overpayment_df = mortgage.overpayment_schedule(overpayment_amount=500, compare=True)
    print(overpayment_df)

    mortgage = OverpaymentCalculator(
        loan_amount=331794,
        fixed_rate=4.55,
        variable_rate=6.99,
        tenure=30,
        fixed_tenure=5,
    )
    print(f'{"="*20} Variable Mortgage Overpayment Calculator {"="*20}')
    overpayment_df = mortgage.overpayment_schedule(overpayment_amount=500)
    print(overpayment_df)

    print(f'{"="*20} Fixed Mortgage Overpayment Calculator {"="*20}')
    mortgage = OverpaymentCalculator(loan_amount=331794, fixed_rate=4.55, tenure=30)
    overpayment_df = mortgage.overpayment_schedule(overpayment_amount=500)
    print(overpayment_df)
