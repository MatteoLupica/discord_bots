import os
import pandas as pd
from config.config import FILE_XLS  # Assuming you have a config file with FILE_XLS defined

class Files:
    # Define default file path and required columns as class attributes.
    DEFAULT_FILE_PATH = FILE_XLS
    DEFAULT_REQUIRED_COLUMNS = [
        "QueueType", "Date", "Lose/Win", "Champ", "KDA", "KP", 
        "Vision Score", "VS/Min", "Ward Placed", "Destroyed", 
        "Control", "GameDuration", "Note"
    ]
    
    def __init__(self, file_path=None, required_columns=None):
        """
        Initialize with a file path and the list of required columns.
        If no file_path or required_columns are provided, defaults are used.
        """
        self.file_path = file_path if file_path is not None else self.DEFAULT_FILE_PATH
        self.required_columns = required_columns if required_columns is not None else self.DEFAULT_REQUIRED_COLUMNS
        self.df = None
        self.load_file()

    def load_file(self):
        """
        Load the Excel file if it exists, ensuring all required columns are present.
        Otherwise, create an empty DataFrame with the required columns.
        """
        if os.path.exists(self.file_path):
            try:
                self.df = pd.read_excel(self.file_path, dtype={"Note": str})
                # Add any missing columns without deleting existing data
                for col in self.required_columns:
                    if col not in self.df.columns:
                        self.df[col] = None
            except Exception as e:
                raise Exception(f"Error loading Excel file: {e}")
        else:
            self.df = pd.DataFrame(columns=self.required_columns)

    def match_exists(self, match_id):
        """
        Check if a match (using its unique identifier stored in 'Note') already exists.
        """
        if "Note" in self.df.columns:
            return str(match_id) in self.df["Note"].astype(str).values
        return False

    def add_rows(self, new_rows):
        """
        Merge new rows with the existing DataFrame.
        
        Parameters:
            new_rows (list): A list of rows (each a list/tuple) following the order of required_columns.
        
        Returns:
            pd.DataFrame: The updated DataFrame.
        """
        if new_rows:
            new_df = pd.DataFrame(new_rows, columns=self.required_columns)
            self.df = pd.concat([self.df, new_df], ignore_index=True)
        return self.df

    def sort_by_date(self, date_column="Date", date_format='%m/%d/%Y'):
        """
        Sort the DataFrame by a date column, converting to and from datetime as needed.
        
        Parameters:
            date_column (str): The name of the date column.
            date_format (str): Format to parse/print the date.
        
        Returns:
            pd.DataFrame: The sorted DataFrame.
        """
        if date_column in self.df.columns:
            self.df[date_column] = pd.to_datetime(self.df[date_column], format=date_format, errors='coerce')
            self.df = self.df.sort_values(by=date_column, ascending=False)
            self.df[date_column] = self.df[date_column].dt.strftime(date_format)
        return self.df

    def save(self):
        """
        Save the DataFrame to the Excel file.
        """
        try:
            self.df.to_excel(self.file_path, index=False)
        except Exception as e:
            raise Exception(f"Error saving Excel file: {e}")
