import re
import os
import time
import openpyxl
import logging
import pytesseract
import pandas as pd

from PIL import Image
from io import BytesIO
from datetime import datetime
from playwright.sync_api import sync_playwright


start_time = time.time()

class CheckContact:
    """
    A class to check for contact details on web pages using Playwright and extract relevant information.
    """
    def __init__(self, file_path: str):
        """
        Initializes the CheckContact class by reading the Excel file.

        :param file_path: Path to the Excel file containing contact details.
        """

        # Setting up the logging configuration
        self.setup_logging()

        self.file_path = file_path
        self.data = self.read_excel()


    def setup_logging(self) -> None:
        """
        Sets up the logging configuration.
        Creates the 'Logs' directory if it doesn't exist and configures the logger.
        """
        if not os.path.exists("Resources/Logs"):
            os.makedirs("Logs")

        log_filename = f"Resources/Logs/check_contact_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_filename),  # Keep only the file handler
            ]
        )

        self.logger = logging.getLogger()

    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)

    def log_error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)

    def read_excel(self) -> list[dict]:
        """
        Reads an Excel file and returns a list of dictionaries, while skipping rows already processed.
        """
        self.log_info(f"Reading data from Excel file: {self.file_path}")

        # Check if output file exists to resume from last progress
        output_file = "Resources/data/output.xlsx"
        if os.path.exists(output_file):
            self.log_info("🔄 Resuming from previous progress...")
            workbook = openpyxl.load_workbook(output_file, data_only=True)
        else:
            workbook = openpyxl.load_workbook(self.file_path, data_only=True)

        sheet = workbook.active
        headers = [cell.value for cell in sheet[1] if cell.value]
        data = []

        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_dict = {}
            for col_index, cell_value in enumerate(row):
                column_name = headers[col_index]
                row_dict[column_name] = str(cell_value).strip() if cell_value else None

            # Skip rows where 'presence_of_fullname' is already filled
            if row_dict.get("presence_of_fullname"):
                continue

            data.append(row_dict)

        return data

    

    def format_phone_number(self, phone: str) -> str:
        """
        Formats the phone number by removing non-digits and specific country codes.
        
        :param phone: The original phone number as a string.
        :return: The formatted phone number or an empty string if the phone is None.
        """

        if not phone:
            return ""  # Return empty string if phone is None or empty

        formatted_phone = re.sub(r'[^\d]', '', phone)  # Remove non-digit characters
        formatted_phone = re.sub(r'^(?:\+358|358)', '', formatted_phone)  # Remove specific country code
        return formatted_phone


    def check_name_on_page(self, page, url: str, first_name: str, last_name: str) -> bool:
        """
        Checks if the given first and last name exist on the page.
        Tries twice if the name is not found on the first attempt.

        :return: True if the name is found, False otherwise.
        """
        
        def find_name():
            page_text = page.content().lower()
            first_name_lower = first_name.lower()
            last_name_lower = last_name.lower()

            full_name = f"{first_name_lower} {last_name_lower}"
            if full_name in page_text:
                return True

            if first_name_lower in page_text and last_name_lower in page_text:
                return True

            if page_text.count(first_name_lower) > 1 or page_text.count(last_name_lower) > 1:
                return True

            return False

        self.log_info(f"\n\n\nChecking for {first_name} {last_name} on {url}...")

        # First attempt
        if find_name():
            self.log_info(f"✅ Found '{first_name} {last_name}' on the first attempt.")
            return True

        self.log_warning(f"⚠️ Name not found on first attempt. Retrying...")

        # Wait and try again
        page.wait_for_timeout(3000)
        page.reload(wait_until="domcontentloaded")

        if find_name():
            self.log_info(f"✅ Found '{first_name} {last_name}' on the second attempt.")
            return True

        # Fallback: check images and alternative text
        name_exists = self.check_image_and_text(page, url, first_name, last_name)

        if name_exists:
            self.log_info(f"✅ '{first_name} {last_name}' found via image or alternative text check.")
        else:
            self.log_warning(f"❌ {first_name} {last_name} not found after two attempts.")

        return name_exists


    def check_image_and_text(self, page, url: str, first_name: str, last_name: str) -> bool:
        """
        Extracts text from images on the page and checks if the given name is present.
        Handles large images gracefully to prevent Tesseract from crashing.

        :return: True if the name is found in the image text, False otherwise.
        """
        self.log_info(f"Checking for image text on {url}...")

        try:
            self.log_info(f"Checking for image text on {url}...")
            screenshot_bytes = page.screenshot(full_page=True)
            img = Image.open(BytesIO(screenshot_bytes))

            # Resize the image if it's too large
            max_width, max_height = 1500, 3000  # Set reasonable limits
            img_width, img_height = img.size
            
            if img_height > max_height:
                scale_factor = max_height / img_height
                new_width = int(img_width * scale_factor)
                img = img.resize((new_width, max_height))
                self.log_info(f"🔄 Resized image to ({new_width}, {max_height}) to fit processing limits.")

            # Extract text from the resized image
            extracted_text = pytesseract.image_to_string(img)

            # Check if the name exists in the extracted text
            name_found = first_name.lower() in extracted_text.lower() and last_name.lower() in extracted_text.lower()
            self.log_info(f"✅ Name found in image: {name_found}")

            return name_found

        except pytesseract.TesseractError as e:
            self.log_error(f"⚠️ Tesseract error: {e} - Skipping image processing.")
            return False  # Continue execution instead of stopping

        except Exception as e:
            self.log_error(f"⚠️ Unexpected error processing image: {e}")
            return False


    def check_job_title_on_page(self, page, url: str, job_title: str) -> bool:
        """
        Checks if the job title is present on the web page.

        :return: True if job title is found, False otherwise.
        """
        page.wait_for_timeout(1000)
        page_text = page.content().lower()

        if job_title in page_text:
            self.log_info(f"✅ Full title '{job_title}' found on the page.")
            return True

        words = job_title.lower().split()
        all_words_found = all(word in page_text for word in words)

        if all_words_found:
            self.log_info(f"✅ All words from title are present in the page content.")
            return True
        else:
            self.log_error(f"❌ Not all words from the title are found on the page.")

        return False

    def extract_phone_numbers(self, page) -> list[str]:
        """
        Extracts phone numbers from the page content.

        :return: A list of extracted phone numbers.
        """
        page_content = page.content()
        phone_number_pattern = r'(\+?\(?\d{1,4}\)?[\s\.-]?\(?\d{1,4}\)?[\s\.-]?\d{1,4}[\s\.-]?\d{1,4})'
        phone_numbers = re.findall(phone_number_pattern, page_content)
        normalized_numbers = [re.sub(r'\D', '', num) for num in phone_numbers]
        return [num for num in normalized_numbers if len(num) > 8]


    def translate_page(self, page, url: str, job_title: str) -> bool:
        """
        Translates the page and checks if the job title exists in the translated content.

        :return: True if job title is found in translated content, False otherwise.
        """
        try:
            translated_url = f"https://translate.google.com/translate?hl=en&sl=auto&u={url}"
            self.log_info(f"🌍 Translating page: {translated_url}...")
            page.goto(translated_url, wait_until="domcontentloaded", timeout=20000)
            page_text = page.content()
            job_title_found = job_title.lower() in page_text.lower()
            self.log_info(f"✅ Job title found in translated content: {job_title_found}")
        except:
            job_title_found = False

        return job_title_found


    def save_results_to_excel(self, output_file: str = "Resources/data/output.xlsx") -> None:
        """
        Saves results to an Excel file, including original phone numbers.
        """
        df = pd.DataFrame(self.data)
        df.to_excel(output_file, index=False)
        self.log_info(f"Saving results to {output_file}...")


    def run(self) -> None:
        """
        Main method to check contact details for each record in the dataset.
        """
        self.log_info("Starting the contact details check...")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            count = 0
            save_interval = 30  # Save results every 30 records

            try:
            #    for entry in self.data:
               for count, entry in enumerate(self.data, start=1):
                    # Set default values
                    entry['presence_of_fullname'] = "No"
                    entry['presence_of_phone'] = "No"
                    entry['presence_of_job_title'] = "No"

                    print(f"✅ Row {count} is completed!")

                    first_name, last_name = entry['first_name'], entry['last_name']
                    original_phone, job_title, url = entry['phone'], entry['job_title'], entry['decision_maker_source']
                    
                    print(f"Firstname: {first_name}")
                    formatted_phone = self.format_phone_number(original_phone)

                    success = False
                    for attempt in range(2):  # Retry loading twice
                        try:
                            self.log_info(f"🔄 Attempt {attempt + 1}: Loading {url} ...")
                            page.goto(url, wait_until="load", timeout=60000)  # 60s timeout
                            success = True
                            break
                        except Exception as e:
                            self.log_error(f"⚠️ Error loading {url}: {e}")

                    if not success:
                        self.log_error(f"❌ Skipping {url} due to repeated load failures.")
                        continue
                    
                    entry['presence_of_fullname'] = "Yes" if self.check_name_on_page(page, url, first_name, last_name) else "No"

                    if entry['presence_of_fullname'] == "Yes":
                        extracted_phones = self.extract_phone_numbers(page)
                        entry['presence_of_phone'] = "Yes" if formatted_phone and formatted_phone in ', '.join(extracted_phones) else "No"
                        self.log_info(f"📲 Phone number '{original_phone}' is found: {entry['presence_of_phone']}")
                        entry['presence_of_job_title'] = "Yes" if self.check_job_title_on_page(page, url, job_title) else "No"

                        if entry['presence_of_job_title'] == "No":
                            entry['presence_of_job_title'] = "Yes" if self.translate_page(page, url, job_title) else "No"
                    else:
                        entry['presence_of_phone'] = "No"
                        entry['presence_of_job_title'] = "No"

                    # Save progress every `save_interval` rows
                    if count % save_interval == 0:
                        self.save_results_to_excel()
                        self.log_info(f"📝 Auto-saved progress at row {count}.")

            except Exception as e:
                self.log_error(f"🚨 Unexpected error: {e}")
                self.save_results_to_excel()
                self.log_info("⚠️ Auto-saved results before exiting due to an error.")

            finally:
                self.save_results_to_excel()
                self.log_info("✅ Final results saved before closing.")
                browser.close()

            self.log_info("Completed the contact details check.")



if __name__ == "__main__":
    checker = CheckContact("Resources/data/details.xlsx")
    checker.run()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")


# It takes 2 hours and 36 minutes to get all the information.
# For 1 minute scraper can get information for around 17rows.