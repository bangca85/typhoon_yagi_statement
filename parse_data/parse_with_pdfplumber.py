import pdfplumber
import re
import csv

# Regular expression to exactly match dates in the format dd/mm/yyyy or d/m/yyyy
date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'

def extract_transaction_data_from_page(page):
    extracted_data = []
    text = page.extract_text()
    print(text)
    if text:
        lines = text.split("\n")
        transaction = {}

        for line in lines:
            # Stop processing content if "Postal address" is found
            if "Postal address" in line:
                break

            date_match = re.fullmatch(date_pattern, line.strip())
            if date_match:
                if transaction and transaction.get("date"):
                    extracted_data.append(transaction)
                    transaction = {}

                transaction["date"] = line.strip()

            elif re.match(r'\d+\.\d+', line) and 'amount' not in transaction:
                transaction["amount"] = line.strip()

            elif re.match(r'\d+\.\d+', line) and 'code' not in transaction:
                transaction["code"] = line.strip()

            elif "code" in transaction:
                transaction["content"] = transaction.get("content", "") + f" {line.strip()}"

        # Append the last transaction if it exists
        if transaction and transaction.get("date"):
            extracted_data.append(transaction)

    return extracted_data

def process_transaction_data(data):
    extracted_data = []
    for items in data:
        data_detail = {}
        data_detail['date'] = items['date']
        amount_text = items.get('amount', '')
        amount_parts = amount_text.split(' ')
        data_detail['amount'] = amount_parts[0] if amount_parts else ''
        content = ' '.join(amount_parts[1:]).strip() 
        if content and items.get('content', ''):
            content += " "
        content += items.get('content', '').strip()
        data_detail['content'] = content.strip()
        data_detail['code'] = items.get('code', '')
        extracted_data.append(data_detail)
    return extracted_data

def save_to_csv(processed_data, output_file):
    # Open the CSV file in append mode
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'code', 'amount', 'content'])

        # Write each processed entry to the CSV file
        for entry in processed_data:
            writer.writerow({
                'date': entry['date'],
                'code': entry.get('code', ''),
                'amount': entry.get('amount', ''),
                'content': entry.get('content', '')
            })

# File path for the PDF and output CSV
pdf_file_path = "data/file.pdf"
output_file = "full_transactions.csv"

# Open the output CSV file in write mode (to write the header)
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['date', 'code', 'amount', 'content'])
    writer.writeheader()

# Process the PDF file page by page
with pdfplumber.open(pdf_file_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        print(f"Processing page {page_num + 1}...")
        raw_data = extract_transaction_data_from_page(page)
        processed_data = process_transaction_data(raw_data)
        # Save the processed data to the CSV
        save_to_csv(processed_data, output_file)

print(f"Data successfully saved to {output_file}")
