from mortgage.calculator import MortgageCalculator
if __name__ == "__main__": 
    fixed_rate_mortgage = MortgageCalculator(331794, 4.55, 30)
    variable_rate_mortgage = MortgageCalculator(331794, 4.55, 30, 6.99, 5)
    amortisation_schedule_1 = fixed_rate_mortgage.amortisation_schedule()
    amortisation_schedule_2 = variable_rate_mortgage.amortisation_schedule()
    #print(amortisation_schedule_1)
    print(amortisation_schedule_2)