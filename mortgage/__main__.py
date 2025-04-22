"""
This script serves as the entry point for the mortgage calculator.
It imports the necessary classes from the `mortgage.calculator` 
module and demonstrates how to use the `OverpaymentCalculator` 
class to calculate overpayments on a mortgage.
"""

from mortgage.calculator import MortgageCalculator, OverpaymentCalculator

def main():
    """
    Main function to run the mortgage calculator.
    OverpaymentCalculator` is instantiated to illustrate 
    how to calculate the effects of making overpayments on a mortgage
    """
  

    # Example usage of the OverpaymentCalculator
    mortgage = OverpaymentCalculator(
        loan_amount=331794, 
        fixed_rate=4.55, 
        tenure=30, 
        fixed_tenure=5,
        variable_rate=6.99,
        overpayment_amount=500,
        compare=True)

    print(mortgage.overpayment_schedule())

if __name__ == "__main__":
    main()

    