# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Email settings
IMAP_SERVER = 'imap.example.com'
EMAIL_ADDRESS = 'your_email@example.com'
EMAIL_PASSWORD = 'your_password'
PROCESSED_FOLDER = 'Processed'

# Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Directory settings
INVOICE_DIR = 'invoices'
PROCESSED_PDF_DIR = 'processed_pdfs'
PROCESSED_MARKDOWN_DIR = 'processed_markdown'
CSV_UPLOADS_DIR = 'csv_uploads'
TEMPLATE_DIR = 'templates'

# Field Mappings
FIELD_MAPPINGS_FILE = 'field_mappings.json'
