import fitz  # PyMuPDF
import re
import csv

# Regular expression to exactly match dates in the format dd/mm/yyyy or d/m/yyyy
date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
def extract_transaction_data_from_page(page_text):
    extracted_data = []
    lines = page_text.split("\n")
    transaction = {}
    in_transaction = False
    
    for i, line in enumerate(lines):
        # Start extracting data only after 'Transactions in detail'
        if "Transactions in detail" in line:
            in_transaction = True
            continue

        # Stop when encountering "Page"
        if "Page" in line:
            break
        if in_transaction:
            date_match = re.fullmatch(date_pattern, line.strip())
            if date_match:
                # Save the previous transaction if it exists
                if transaction and transaction.get("date"):
                    extracted_data.append(transaction)
                    transaction = {}
                # Start a new transaction with the date
                transaction["date"] = line.strip()
            elif re.match(r'\d+\.\d+', line) and 'code' not in transaction:
                transaction["code"] = line.strip()
            elif re.match(r'\s*\d+\.\d+', line) and 'amount' not in transaction:
                transaction["amount"] = line.strip()
            elif "amount" in transaction:
                transaction["content"] = transaction.get("content", "") + f" {line.strip()}"
    if transaction and transaction.get("date"):
        extracted_data.append(transaction)

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
pdf_file_path = "data/file2.pdf"
output_file = "full_transactions.csv"

# Open the output CSV file in write mode (to write the header)
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['date', 'code', 'amount', 'content'])
    writer.writeheader()

# Process the PDF file page by page using PyMuPDF
doc = fitz.open(pdf_file_path)
for page_num in range(doc.page_count):
    print(f"Processing page {page_num + 1}...")
    page = doc.load_page(page_num)
    page_text = page.get_text("text") 
    raw_data = extract_transaction_data_from_page(page_text)
    save_to_csv(raw_data, output_file)

print(f"Data successfully saved to {output_file}")
