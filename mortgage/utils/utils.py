"""
utils.py
Utility functions for the mortgage application.
"""

import os
from functools import wraps
from datetime import datetime
from mortgage.helpers import _mortgage_summary


def output_csv(func):
    """
    Decorator to save the output of a function to a CSV file.
    This decorator creates an 'output_files' directory if it doesn't exist,
    and saves the DataFrame returned by the function to a CSV file with a
    timestamped filename.
    Args:
        func (callable): The function to be decorated, which should return a pandas DataFrame.
    Returns:
        callable: The wrapped function that saves its output to a CSV file.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Ensure output directory exists
        os.makedirs("output_files", exist_ok=True)

        # Get DataFrame from decorated function
        data_frame = func(*args, **kwargs)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y_%m%d_%H%M%S")
        filename = f"{func.__name__}_{timestamp}.csv"
        filepath = os.path.join("output_files", filename)

        # Save DataFrame to CSV
        with open(filepath, "w", encoding="utf-8") as file:
            # Write summary first if available
            summary_lines = _mortgage_summary(args[0], data_frame, compare=True)
            for line in summary_lines:
                file.write(line + "\n")
            file.write("\n")
            data_frame.to_csv(
                file, index=False
            )  # Write DataFrame to the same file object

        print(f"Saved CSV to: {filepath}")
        return data_frame

    return wrapper
