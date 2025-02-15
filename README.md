📅 Project Overview:

This project focuses on verifying contact details (such as names, phone numbers, and job titles) across various web pages. The goal is to automate the process of checking if the given contact information appears correctly on the web, ensuring accuracy and saving time for the client in gathering this data.

🔔 How the Project Works (Technical Explanation):
The system operates by reading contact details from an Excel file. For each record, the program:
    1️⃣. Reads Data from Excel: The contact information is extracted from the Excel sheet, which includes first and last names, phone numbers, job titles, and web page URLs.
    2️⃣. Automates Web Navigation: Using Playwright (a browser automation tool), the program navigates to each URL provided in the Excel file and loads the page.
    3️⃣. Checks for Names and Job Titles: The program verifies if the provided name and job title appear on the page. It checks both plain text content and images (if the name might be part of an image or screenshot on the webpage).
    4️⃣. Extracts Phone Numbers: The script looks for any phone numbers on the page and checks if the provided phone number is present. It formats the phone number to handle various formats and inconsistencies.
    5️⃣. Translates Pages if Needed: If the webpage is in a different language, the program can automatically translate the page to check for the presence of the job title in the translated content.
    6️⃣. Records Results: After the checks, the results (whether the name, job title, and phone number were found on the page) are saved to a new Excel file for easy review.

🔔 Human-Friendly Overview:
This project is designed to automate the process of verifying contact information across multiple websites. Instead of manually visiting each website and looking for the relevant details, this tool does the hard work for you!

Here’s what happens step by step:
    1️⃣. Data Collection: You provide a list of people’s contact details in an Excel file, including their names, job titles, phone numbers, and the URLs where this information is expected to appear.
    2️⃣. Web Search Automation: The tool then automatically opens each webpage listed, looking for the person’s name, job title, and phone number. It even checks if the name appears in images (in case it’s displayed as a picture rather than text on the page).
    3️⃣. Phone Number Detection: If there’s a phone number listed on the page, the tool compares it with the one in your Excel file to confirm it matches.
    4️⃣. Job Title Verification: The program checks if the job title is listed on the webpage. If the page is in a foreign language, it can translate the page and check again.
    5️⃣. Results Reporting: Finally, all the checks are documented in a new Excel file. This way, you can quickly see if all the details match and ensure that the contact information is accurate.


📂 Installation Guide

1. Prerequisites

    Ensure the following are installed:

    🔹 Git – Check by running:
        git --version

    If not installed:

        Windows: Download from git-scm.com
        macOS: Install via Homebrew:
        brew install git

    🔹 Python 3.11+ – Check by running:
   
       python --version

   If not installed, download from python.org

3. Clone the Repository
    Navigate to your desired directory and run:

       git clone https://github.com/Up-Bizz/ContactVerifier.git
       cd ContactVerifier

5. Set Up a Virtual Environment:

       Windows (CMD/PowerShell):
           python -m venv venv
           venv\Scripts\activate

       macOS/Linux:
           python3 -m venv venv
           source venv/bin/activate

7. Install Dependencies:

       pip install -r requirements.txt or pip3 install -r requirements.txt

9. Install Playwright and Browsers:

       playwright install

11. Install Tesseract-OCR:

        Windows:
           1. Download from Tesseract-OCR.
           2. Add the installation path to your system PATH.

        Linux (Ubuntu/Debian):
           sudo apt update && sudo apt install -y tesseract-ocr
        
        macOS (Homebrew):
           brew install tesseract

   Verify Installation:
       
       tesseract --version

11. Run the Script:

        python check_contact.py or python3 check_contact.py


📌 Summary

✅ Clone Repository
✅ Set Up Virtual Environment
✅ Install Dependencies
✅ Install Playwright & Browsers
✅ Install Tesseract-OCR
✅ Run the Script


