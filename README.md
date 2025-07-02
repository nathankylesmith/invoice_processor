# Invoice Processing Automation

This script automates the processing of PDF invoices from emails by using the Gemini AI to intelligently extract data.

## Features

- Fetches PDF invoices from a specified email account.
- Uses the Gemini 1.5 Flash model to perform OCR and structured data extraction in one step.
- Creates a clean Markdown version of each invoice.
- Creates two different, template-based CSV files for uploading to other systems.
- Uses a predefined list of values for specific fields (e.g., 'account', 'project') to ensure data consistency.
- Moves processed emails and PDF files to designated folders to prevent reprocessing.

## Setup Instructions

These instructions cover how to set up and run the project on both macOS and Windows.

### 1. Clone the Repository

First, clone the repository to your local machine using Git.

```bash
git clone https://github.com/nathankylesmith/invoice_processor.git
cd invoice_processor
```

### 2. Create and Configure Environment Files

- **Create a `.env` file** in the `invoice_processor` directory. This file will store your secret API key. Add the following line to it, replacing `YOUR_API_KEY_HERE` with your actual Gemini API key:
  ```
  GEMINI_API_KEY=YOUR_API_KEY_HERE
  ```
- **Update `config.py`** with your email server details (`IMAP_SERVER`, `EMAIL_ADDRESS`, `EMAIL_PASSWORD`).
- **Update `field_mappings.json`** with the allowed values for your accounts and projects. The AI will be forced to choose from these lists.
- **Update CSV templates** in the `templates/` directory to match the exact headers your other systems require.

### 3. Set Up a Virtual Environment and Install Dependencies

Using a virtual environment is highly recommended to keep project dependencies isolated.

**On macOS:**
```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

**On Windows:**
```bash
# Create the virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt
```
*(You should see `(venv)` at the beginning of your terminal prompt after activation.)*

### 4. Run the Script

Once everything is configured and dependencies are installed, you can run the script from your terminal:

```bash
python invoice_processor.py
```

The script will log its progress in the terminal, indicating which invoices are being processed and when it's finished.
