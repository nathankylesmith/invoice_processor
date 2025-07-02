# Invoice Processing Automation

This script automates the processing of PDF invoices from emails.

## Features

- Fetches invoices from a specified email account.
- Moves processed emails to a designated folder.
- Performs OCR on the PDF invoices.
- Extracts and saves the invoice content as Markdown.
- Creates two different CSV files for uploading to other systems.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure email:**
    Update the `config.py` file with your email server details and credentials.

3.  **Run the script:**
    ```bash
    python invoice_processor.py
    ```
