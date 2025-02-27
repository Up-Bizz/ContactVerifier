import os
import argparse
import pandas as pd

def split_excel_file(input_file, output_dir="Resources/data", to_csv=False):  
    """
    Splits an Excel file into three parts and saves them as separate files.
    
    :param input_file: Path to the input Excel file.
    :param output_dir: Directory to save output files (default: Resources/data).
    :param to_csv: If True, saves output files as CSV instead of Excel.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        df = pd.read_excel(input_file)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return  
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    total_rows = len(df)
    rows_per_file = total_rows // 3

    base_name = os.path.basename(input_file).replace(".xlsx", "")  
    file_extension = "csv" if to_csv else "xlsx"
    
    file_names = [os.path.join(output_dir, f"{i:02d}_{base_name}.{file_extension}") for i in range(1, 4)]

    df1, df2, df3 = df.iloc[:rows_per_file], df.iloc[rows_per_file:2 * rows_per_file], df.iloc[2 * rows_per_file:]

    try:
        if to_csv:
            df1.to_csv(file_names[0], index=False)
            df2.to_csv(file_names[1], index=False)
            df3.to_csv(file_names[2], index=False)
        else:
            df1.to_excel(file_names[0], index=False)
            df2.to_excel(file_names[1], index=False)
            df3.to_excel(file_names[2], index=False)

        print(f"Successfully split '{input_file}' into folder {output_dir}:")
        for file_name in file_names:
            print(f"- {file_name}")

    except Exception as e:
        print(f"Error writing files: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split an Excel file into three parts.")
    parser.add_argument("input_file", help="Path to the input Excel file")
    parser.add_argument("-o", "--output_dir", help="Directory to save output files (default: Resources/data)", default="Resources/data")
    parser.add_argument("--to_csv", action="store_true", help="Save output files as CSV instead of Excel")

    args = parser.parse_args()
    
    split_excel_file(args.input_file, args.output_dir, args.to_csv)
