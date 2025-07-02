# invoice_processor.py

import os
import imapclient
import pyzmail
import email
import json
import pandas as pd
import google.generativeai as genai
from config import *

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def connect_to_email():
    """Connects to the email server and returns an IMAP client."""
    try:
        client = imapclient.IMAPClient(IMAP_SERVER, ssl=True)
        client.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        return client
    except Exception as e:
        print(f"Error connecting to email: {e}")
        return None

def fetch_invoices(client):
    """Fetches new emails with PDF invoices."""
    try:
        client.select_folder('INBOX', readonly=False)
        uids = client.search(['NOT', 'DELETED'])
        raw_messages = client.fetch(uids, ['BODY[]', 'FLAGS'])
        return raw_messages, uids
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return None, None

def process_email(raw_message):
    """Processes a single email and extracts the PDF attachment."""
    msg = pyzmail.PyzMessage.factory(raw_message[b'BODY[]'])
    for part in msg.mailparts:
        if part.media_maintype == 'application' and part.media_subtype == 'pdf':
            filename = part.filename
            if filename:
                pdf_path = os.path.join(INVOICE_DIR, filename)
                with open(pdf_path, 'wb') as f:
                    f.write(part.get_payload())
                print(f"Saved invoice: {filename}")
                return pdf_path
    return None

def get_invoice_data_with_gemini(pdf_path, field_mappings):
    """Uses Gemini to extract data from the PDF and get a markdown version."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Analyze the attached invoice PDF. Your goal is to do two things:

        1.  Create a clean, well-formatted markdown version of the entire invoice.
        2.  Extract the following key-value pairs from the invoice and return them as a JSON object.

        Here are the fields to extract:
        - invoice_number
        - invoice_date
        - total_amount
        - vendor_name
        - account
        - project

        For the 'account' and 'project' fields, you MUST choose the most appropriate value from the lists provided below. Do not invent new values.

        Allowed 'account' values: {field_mappings['accounts']}
        Allowed 'project' values: {field_mappings['projects']}

        Your final output should be a single JSON object with two keys: "markdown" and "data".
        Example:
        {{
            "markdown": "# Invoice\n\n**Vendor:** ACME Corp... ",
            "data": {{
                "invoice_number": "12345",
                "invoice_date": "2025-07-01",
                "total_amount": "99.99",
                "vendor_name": "ACME Corp",
                "account": "Account B",
                "project": "Project Y"
            }}
        }}
        """
        invoice_file = genai.upload_file(path=pdf_path, display_name=os.path.basename(pdf_path))
        response = model.generate_content([prompt, invoice_file])

        # Clean up the response from Gemini, which might include backticks and 'json'
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        result = json.loads(cleaned_response)
        return result['markdown'], result['data']

    except Exception as e:
        print(f"Error processing with Gemini for {pdf_path}: {e}")
        return None, None

def save_as_markdown(markdown_content, pdf_path):
    """Saves the extracted markdown content to a file."""
    if not markdown_content:
        return
    try:
        filename = os.path.basename(pdf_path)
        markdown_filename = os.path.splitext(filename)[0] + '.md'
        markdown_path = os.path.join(PROCESSED_MARKDOWN_DIR, markdown_filename)
        with open(markdown_path, 'w') as f:
            f.write(markdown_content)
        print(f"Saved markdown: {markdown_filename}")
    except Exception as e:
        print(f"Error saving markdown for {pdf_path}: {e}")


def create_csv_from_template(data, template_file, output_filename):
    """Creates a CSV file based on a template and extracted data."""
    try:
        template_path = os.path.join(TEMPLATE_DIR, template_file)
        output_path = os.path.join(CSV_UPLOADS_DIR, output_filename)

        # Read the headers from the template
        template_df = pd.read_csv(template_path)
        headers = template_df.columns

        # Create a new DataFrame with the extracted data, ensuring all template columns are present
        output_data = {header: data.get(header.lower().replace(' ', '_')) for header in headers}
        output_df = pd.DataFrame([output_data])

        output_df.to_csv(output_path, index=False)
        print(f"Created CSV: {output_filename}")

    except Exception as e:
        print(f"Error creating CSV {output_filename}: {e}")


def move_file(src_path, dest_dir):
    """Moves a file to a destination directory."""
    try:
        filename = os.path.basename(src_path)
        new_path = os.path.join(dest_dir, filename)
        os.rename(src_path, new_path)
        print(f"Moved {filename} to {dest_dir}")
    except Exception as e:
        print(f"Error moving file {src_path}: {e}")

def move_email_to_processed(uid, client):
    """Moves an email to the processed folder."""
    try:
        client.move(uid, PROCESSED_FOLDER)
        print(f"Moved email {uid} to {PROCESSED_FOLDER}")
    except Exception as e:
        print(f"Error moving email {uid}: {e}")


def main():
    """Main function to run the invoice processing workflow."""
    # Load field mappings
    try:
        with open(FIELD_MAPPINGS_FILE, 'r') as f:
            field_mappings = json.load(f)
    except Exception as e:
        print(f"Error loading field mappings from {FIELD_MAPPINGS_FILE}: {e}")
        return

    client = connect_to_email()
    if not client:
        return

    raw_messages, uids = fetch_invoices(client)
    if not raw_messages:
        print("No new invoices found.")
        client.logout()
        return

    for uid, message_data in raw_messages.items():
        pdf_path = process_email(message_data)
        if pdf_path:
            print(f"Processing {pdf_path} with Gemini...")
            markdown, data = get_invoice_data_with_gemini(pdf_path, field_mappings)

            if markdown and data:
                save_as_markdown(markdown, pdf_path)
                base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
                create_csv_from_template(data, 'system1_template.csv', f"{base_filename}_system1.csv")
                create_csv_from_template(data, 'system2_template.csv', f"{base_filename}_system2.csv")
                move_file(pdf_path, PROCESSED_PDF_DIR)
                move_email_to_processed(uid, client)
            else:
                print(f"Failed to process {pdf_path} with Gemini. Skipping.")

    client.logout()

if __name__ == '__main__':
    main()