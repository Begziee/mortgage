import os
from functools import wraps
from datetime import datetime

def output_csv(func):
    """
    Decorator to save the output of a function to a CSV file.
    The CSV file will be named after the function with a timestamp.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Ensure output directory exists
        os.makedirs("output_files", exist_ok=True)

        # Get DataFrame from decorated function
        df = func(*args, **kwargs)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y_%m%d_%H%M%S")
        filename = f"{func.__name__}_{timestamp}.csv"
        filepath = os.path.join("output_files", filename)

        # Save DataFrame to CSV
        df.to_csv(filepath, index=False)
        print(f"Saved CSV to: {filepath}")
        return df
    return wrapper