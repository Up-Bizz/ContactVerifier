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


## Organize the Project Structure
CheckContactProject/
│── Resources/
│   │── data/
│   │   ├── details.xlsx  (Input file)
│   │── Logs/  (Generated logs)
│── Scripts/
│── .gitignore
│── README.md
│── requirements.txt
│── check_contact.py  (Main class)


📌 Project Setup Guide
1. Install Required Software

Before proceeding, ensure you have the following installed:
    - Python 3.11+ (Check with python --version)
    - pip (Python package manager, should be installed with Python)
    - virtualenv (for creating an isolated environment)
    - Google Chrome (for Playwright to work properly)
    - Tesseract OCR (for image text extraction)

2. Clone the Repository
    - If the client receives the code as a ZIP file, they should extract it. If using Git:
git clone <REPOSITORY_URL>
cd <PROJECT_FOLDER>


3. Create and Activate a Virtual Environment

Windows (CMD or PowerShell)
python -m venv venv
venv\Scripts\activate

Mac/Linux (Terminal)
python3 -m venv venv
source venv/bin/activate


4. Install Dependencies
Run the following command to install all required packages:
pip install -r requirements.txt

or 

pip install openpyxl logging pytesseract pandas pillow playwright


5. Install Playwright Browsers
After installing dependencies, install Playwright browsers:
playwright install


6. Install Tesseract OCR
Tesseract is required for image-based text extraction.
Windows
    Download from: https://github.com/UB-Mannheim/tesseract/wiki
    Install it and note the installation path (e.g., C:\Program Files\Tesseract-OCR).
    Add this path to the system environment variables (PATH).
    Verify installation by running:
tesseract --version

Mac (Homebrew)
brew install tesseract