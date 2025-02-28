import os
import argparse
import sqlite3
import pandas as pd


def convert_file_to_db(filename: str, db_filename: str = None):
    """
    Converts a CSV or XLSX file into an SQLite database.
    """
    if db_filename is None:
        db_filename = filename.rsplit('.', 1)[0] + '.db'
    
    if filename.endswith('.csv'):
        df = pd.read_csv(filename)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(filename)
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or XLSX file.")
    
    conn = sqlite3.connect(db_filename)
    df.to_sql('contacts', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print(f"✅ File data successfully converted to {db_filename}")


def convert_db_to_file(db_filename: str, output_filename: str):
    """
    Converts a SQLite database table into a CSV or XLSX file.
    """
    if not os.path.exists(db_filename):
        raise FileNotFoundError(f"Database file '{db_filename}' not found.")
    
    if not (output_filename.endswith('.csv') or output_filename.endswith('.xlsx')):
        raise ValueError("Output file must be either .csv or .xlsx")
    
    conn = sqlite3.connect(db_filename)
    df = pd.read_sql_query("SELECT * FROM contacts", conn)
    conn.close()
    
    if output_filename.endswith('.csv'):
        df.to_csv(output_filename, index=False)
    else:
        df.to_excel(output_filename, index=False)
    print(f"✅ Database exported to {output_filename}")


def main():
    parser = argparse.ArgumentParser(description="Convert CSV/XLSX to SQLite or vice versa.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subparser for converting file to database
    parser_file_to_db = subparsers.add_parser("file-to-db", help="Convert CSV/XLSX to SQLite DB")
    parser_file_to_db.add_argument("filename", help="Input CSV or XLSX file")
    parser_file_to_db.add_argument("--db_filename", help="Optional database filename")

    # Subparser for converting database to file
    parser_db_to_file = subparsers.add_parser("db-to-file", help="Convert SQLite DB to CSV/XLSX")
    parser_db_to_file.add_argument("db_filename", help="Input database filename")
    parser_db_to_file.add_argument("output_filename", help="Output CSV or XLSX filename")

    args = parser.parse_args()
    
    if args.command == "file-to-db":
        convert_file_to_db(args.filename, args.db_filename)
    elif args.command == "db-to-file":
        convert_db_to_file(args.db_filename, args.output_filename)

if __name__ == "__main__":
    main()


"""

Convert CSV/XLSX to SQLite DB
    python utils.py file-to-db name_of_file.csv --db_filename name_of_file.db
(If --db_filename is not provided, it defaults to details.db)

Convert SQLite DB to CSV/XLSX
    python utils.py db-to-file name_of_file.db name_of_file.xlsx
(Specify .csv or .xlsx for the output)

"""