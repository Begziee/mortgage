# Mortgage Simulator

## Motivation

There are many conflicting opinions about mortgages. One school of thought questions the need to commit to a mortgage, especially when monthly payments are often three times the current rent. Another perspective encourages paying off your mortgage early by making overpayments, while some suggest investing those extra funds in the stock market for potentially higher returns. However, stock market investments come with higher volatility and risk.

**This project was created to help you:**
- Simulate your mortgage payment schedule.
- Calculate the effect of making overpayments.
- Track your daily mortgage balance.
- Compare the impact of overpaying your mortgage versus following the standard payment plan.

The goal is to provide a clear, data-driven way to understand your mortgage options and make informed financial decisions.

---

## Features

- **Flexible Mortgage Simulation:** Enter your loan amount, interest rates (fixed and variable), tenure, and payment schedule.
- **Overpayment Analysis:** See how making extra payments affects your total interest paid and loan duration.
- **Daily Balance Calculation:** Track your mortgage balance on a daily basis.
- **Comparison Tools:** Compare standard payments, overpayments, and alternative investment scenarios.

---

## Getting Started

### Prerequisites

- Python 3.8+
- [pandas](https://pandas.pydata.org/)
- [numpy](https://numpy.org/)
- [matplotlib](https://matplotlib.org/) (optional, for plotting)
- [openpyxl](https://openpyxl.readthedocs.io/) (optional, for Excel export)

Install dependencies with:
```bash
pip install pandas numpy matplotlib openpyxl
```

---

### Usage

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Begziee/mortgage.git
    cd mortgage
    ```

2. **Prepare your payment schedule:**
    - Create a CSV file (e.g., `payment_schedule.csv`) with columns:  
      `payment_date,amount`  
      Example:
      ```
      16/12/2024,2350.98
      02/01/2025,1691.02
      ```

3. **Run the simulation:**
    ```bash
    python mortgage/calculator.py
    ```

4. **View results:**
    - Results are printed to the console or exported to CSV/Excel as configured.

---

## Example

```python
from mortgage.calculator import MortgageBalance

mb = MortgageBalance(
    loan_amount=300000,
    fixed_rate=3.5,
    start_date="01/01/2024",
    payment_link="payment_schedule.csv",
    tenure=25,
    today_payment=2000
)

df = mb._daily_balance()
print(df.head())
```

---

## Project Structure

```
mortgage/
├── calculator.py
├── helpers/
│   └── helpers.py
├── payment_schedule.csv
├── README.md
└── ...
```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.


---

## Contact

For questions or suggestions, please open an issue or contact the maintainer.
