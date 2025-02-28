import sqlite3
import os 
import pandas as pd 
import re
import time
import openpyxl
import argparse
import logging
import pytesseract

from PIL import Image
from io import BytesIO
from datetime import datetime
from playwright.sync_api import sync_playwright
from check_contact import CheckContact

start_time = time.time()

statuses = {
    'not_processed': 'not_processed',
    'processing': 'processing',
    'processed': 'processed',
    'error': 'error'
}

class DB:
    db_name = "details.db"

    @staticmethod
    def database_exists():
        """Checks if the database file exists."""
        return os.path.exists(DB.db_name)
    
    @staticmethod
    def initialize_db_if_needed(file_path='details.xlsx'):
        """
        Checks if the database exists. If it does not exist, creates it and inserts data.
        If the database already exists, does nothing.
        """
        if DB.database_exists():
            print("✅ Database already exists. No action needed.")
        else:
            print("🛠️ Database does not exist. Creating and populating...")
            DB.create_database()
            DB.read_excel_and_store(file_path)
            print("✅ Database initialized successfully.")
    
    @staticmethod
    def create_database():
        """Creates a SQLite database table if it doesn't exist."""
        conn = sqlite3.connect(DB.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                job_title TEXT,
                decision_maker_source TEXT,
                presence_of_fullname BOOLEAN DEFAULT 0,
                presence_of_phone BOOLEAN DEFAULT 0,
                presence_of_job_title BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'not_processed',  -- Tracks progress
                error TEXT  -- Stores any errors
            )
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def read_excel_and_store(file_path='details.xlsx'):
        """
        Reads an Excel file and stores the data in SQLite.
        Avoids duplicate entries using the UNIQUE constraint.

        :param file_path: Path to the Excel file.
        """
        print(f"📂 Reading data from Excel file: {file_path}")

        # Ensure file exists
        if not os.path.exists(file_path):
            print(f"🚨 Error: File '{file_path}' not found.")
            raise FileNotFoundError(f"File '{file_path}' not found.")

        # Read Excel file
        try:
            df = pd.read_excel(file_path, dtype=str)  # Ensure all data is read as strings
        except Exception as e:
            print(f"⚠️ Failed to open Excel file: {e}")
            raise ValueError(f"Error opening Excel file: {e}")

        # Fill NaN values with None
        df = df.where(pd.notna(df), None)

        # Connect to SQLite
        conn = sqlite3.connect(DB.db_name)
        cursor = conn.cursor()

        # ✅ Ensure the table exists
        DB.create_database()

        # Insert each row into the database
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO contacts (first_name, last_name, phone, job_title, decision_maker_source)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['first_name'], row['last_name'], row['phone'], row['job_title'], row['decision_maker_source']))
            except sqlite3.IntegrityError:
                print(f"⚠️ Skipping duplicate entry: {row['first_name']} {row['last_name']}")

        # Commit and close the database connection
        conn.commit()
        conn.close()

        print(f"✅ Data from {file_path} has been successfully inserted into the database.")
    
    @staticmethod
    def get_first_not_processed(status="'not_processed'") -> dict:
        """Fetch the first row where status='not_processed'"""
        conn = sqlite3.connect(DB.db_name)
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT * FROM contacts
            WHERE status = {status}
            ORDER BY id ASC
            LIMIT 1;
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "phone": row[3],
                "job_title": row[4],
                "decision_maker_source": row[5],
                "presence_of_fullname": row[6],
                "presence_of_phone": row[7],
                "presence_of_job_title": row[8],
                "status": row[9],
                "error": row[10]
            }
        else:
            return None  # No unprocessed rows found


    @staticmethod
    def update_status_by_id(row_id, row='status', status="processing", log_info=True):
        """
        Updates the status of a row in the database by ID.
        
        :param row_id: The ID of the row to update.
        :param status: The new status (default: "processing").
        """
        conn = sqlite3.connect(DB.db_name)
        cursor = conn.cursor()

        cursor.execute(f"""
            UPDATE contacts 
            SET {row} = ?
            WHERE id = ?;
        """, (status, row_id))

        conn.commit()
        conn.close()
        if log_info:
            print(f"✅ Updated row {row_id} to status '{status}'")


    @staticmethod
    def save_db_to_csv_excel(to_csv=True, to_excel=True):
        """
        Exports the database table to CSV and/or Excel.

        :param output_dir: Directory to save output files (default: "exports").
        :param to_csv: If True, saves the file as CSV (default: True).
        :param to_excel: If True, saves the file as Excel (default: True).
        """

        # Ensure the output directory exists

        # Connect to SQLite and fetch data
        conn = sqlite3.connect(DB.db_name)
        query = "SELECT * FROM contacts"
        df = pd.read_sql_query(query, conn)
        conn.close()

        csv_path = DB.db_name.replace('.db', '.csv')
        excel_path = DB.db_name.replace('.db', '.xlsx')
        # Save to CSV
        if to_csv:
            df.to_csv(csv_path, index=False)
            print(f"✅ Database exported to CSV: {csv_path}")

        # Save to Excel
        if to_excel:
            df.to_excel(excel_path, index=False)
            print(f"✅ Database exported to Excel: {excel_path}")


class CheckContact(CheckContact):

    def __init__(self, file_path, db_name=None):
        self.setup_logging()
        self.round_count = 0
        DB.db_name = db_name if db_name else file_path.replace('.xlsx', '.db')
        DB.initialize_db_if_needed(file_path)

    def run(self) -> None:
        """
        Main method to check contact details for each record in the dataset.
        """
        self.log_info("Starting the contact details check...")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            processing_row = DB.get_first_not_processed()
            
            while processing_row:
                try:
                    url, first_name, last_name, phone_number, job_title = processing_row['decision_maker_source'], processing_row['first_name'], processing_row['last_name'], processing_row['phone'], processing_row['job_title']
                    formatted_phone = self.format_phone_number(phone_number)
                    DB.update_status_by_id(processing_row['id'], log_info=False) # changes status to processing
                    print(f"Processing: {first_name}")
                    success = False
                    for attempt in range(2):  # Retry loading twice
                        try:
                            # print(f"🔄 Attempt {attempt + 1}: Loading {url} ...")
                            page.goto(url, wait_until="load", timeout=60000)  # 60s timeout
                            success = True
                            break
                        except Exception as e:
                            self.log_error(f"⚠️ Error loading {url}: {e}")
                    
                    if not success:
                        self.log_error(f"❌ {url} updated error due to repeated load failures.")
                        DB.update_status_by_id(processing_row['id'], status=statuses['error'])
                        DB.update_status_by_id(processing_row['id'], row='error', status="After 2 attempts, did not reach website.")
                    else: 
                        print(f'Success for url: {url}')
                        print('Checking for name, phone, job_title')
                        presence_of_fullname = True if self.check_name_on_page(page, url, first_name, last_name) else False
                        if presence_of_fullname:
                            extracted_phones = self.extract_phone_numbers(page)
                            presence_of_phone = True if formatted_phone and formatted_phone in ', '.join(extracted_phones) else False
                            presence_of_job_title = True if self.check_job_title_on_page(page, url, job_title) else False

                            if not presence_of_job_title:
                                presence_of_job_title = True if self.translate_page(page, url, job_title) else False

                        else:
                            presence_of_phone = False 
                            presence_of_job_title = False
                        
                        print(f'Found name: {presence_of_fullname}, job_title: {presence_of_job_title}, phone: {presence_of_phone}')

                        DB.update_status_by_id(processing_row['id'], row='presence_of_fullname', status=presence_of_fullname, log_info=False)
                        DB.update_status_by_id(processing_row['id'], row='presence_of_job_title', status=presence_of_job_title, log_info=False)
                        DB.update_status_by_id(processing_row['id'], row='presence_of_phone', status=presence_of_phone, log_info=False)
                        DB.update_status_by_id(processing_row['id'], status=statuses['processed'])
                    
                    print(f"{first_name} info saved!")
                    processing_row = DB.get_first_not_processed() 

                except Exception as e:
                    print("ERROR: ", e)
                    self.log_error(f"🚨 Unexpected error: {e}")
                    DB.update_status_by_id(processing_row['id'], status=statuses['not_processed'])

            print("✅ Final results saved before closing.")
            browser.close()
            print("Completed the contact details check.")
            DB.save_db_to_csv_excel()


# check_contact = CheckContact(file_path='details2.xlsx')
# check_contact.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CheckContact with custom Excel and DB filenames.")
    parser.add_argument("excel_file", type=str, help="Path to the Excel file (e.g., details.xlsx)")
    parser.add_argument("--db_name", type=str, default=None, help="Custom SQLite database filename (default: same as Excel file)")

    args = parser.parse_args()

    check_contact = CheckContact(file_path=args.excel_file, db_name=args.db_name)
    check_contact.run()


"""
    How to Run from Terminal:

    python script.py details.xlsx --db_name my_database.db

    or, if you want the database name to match the Excel file:

    python script.py details.xlsx
"""