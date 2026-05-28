import csv
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import re


class TransactionCSVParser:
    """
    A specialized class to parse financial transaction CSV files and convert them to JSON format.
    Designed for CSV format: Transaction Date,Post Date,Description,Category,Type,Amount,Memo
    """

    def __init__(self, csv_file_path: str, json_file_path: str):
        """
        Initialize the parser with input and output file paths.

        Args:
            csv_file_path (str): Path to the input CSV file
            json_file_path (str): Path to the output JSON file
        """
        self.csv_file_path = Path(csv_file_path)
        self.json_file_path = Path(json_file_path)
        self.transactions = []
        self.raw_data = []

    def read_csv(self, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        Read transaction CSV file and store raw data.

        Args:
            encoding (str): File encoding (default: 'utf-8')

        Returns:
            List[Dict[str, Any]]: List of raw transaction dictionaries
        """
        try:
            with open(self.csv_file_path, 'r', encoding=encoding, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                self.raw_data = [row for row in reader]

            print(f"Successfully read {len(self.raw_data)} transaction records from {self.csv_file_path}")
            return self.raw_data

        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")

    def parse_date(self, date_string: str) -> str:
        """
        Parse date string from MM/DD/YYYY format to ISO format.

        Args:
            date_string (str): Date in MM/DD/YYYY format

        Returns:
            str: Date in YYYY-MM-DD format, or original string if parsing fails
        """
        if not date_string or date_string.strip() == '':
            return None

        try:
            # Parse MM/DD/YYYY format
            parsed_date = datetime.strptime(date_string.strip(), '%m/%d/%Y')
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            print(f"Warning: Could not parse date '{date_string}', keeping original format")
            return date_string.strip()

    def parse_amount(self, amount_string: str) -> float:
        """
        Parse amount string to float, handling negative values and currency symbols.

        Args:
            amount_string (str): Amount string (e.g., '-17.92', '$100.00')

        Returns:
            float: Parsed amount
        """
        if not amount_string or amount_string.strip() == '':
            return 0.0

        try:
            # Remove currency symbols and whitespace
            cleaned_amount = re.sub(r'[^\d.-]', '', amount_string.strip())
            return float(cleaned_amount)
        except ValueError:
            print(f"Warning: Could not parse amount '{amount_string}', defaulting to 0.0")
            return 0.0

    def clean_description(self, description: str) -> str:
        """
        Clean up transaction description by removing extra whitespace.

        Args:
            description (str): Raw description

        Returns:
            str: Cleaned description
        """
        if not description:
            return ""
        return ' '.join(description.strip().split())

    def determine_transaction_type(self, type_field: str, amount: float) -> Dict[str, Any]:
        """
        Determine transaction type and add additional metadata.

        Args:
            type_field (str): Original type field from CSV
            amount (float): Transaction amount

        Returns:
            Dict[str, Any]: Dictionary with type info and metadata
        """
        type_info = {
            'original_type': type_field.strip() if type_field else '',
            'is_debit': amount < 0,
            'is_credit': amount > 0,
            'abs_amount': abs(amount)
        }

        # Standardize transaction type
        if type_field:
            type_lower = type_field.lower().strip()
            if type_lower in ['sale', 'debit', 'purchase']:
                type_info['standardized_type'] = 'debit'
            elif type_lower in ['credit', 'deposit', 'refund', 'payment']:
                type_info['standardized_type'] = 'credit'
            else:
                type_info['standardized_type'] = type_lower
        else:
            type_info['standardized_type'] = 'debit' if amount < 0 else 'credit'

        return type_info

    def transform_transactions(self) -> List[Dict[str, Any]]:
        """
        Transform raw CSV data into structured transaction objects.

        Returns:
            List[Dict[str, Any]]: List of transformed transaction dictionaries
        """
        self.transactions = []

        for i, raw_transaction in enumerate(self.raw_data):
            try:
                # Parse amount first as it's used in type determination
                amount = self.parse_amount(raw_transaction.get('Amount', '0'))

                # Get type information
                type_info = self.determine_transaction_type(
                    raw_transaction.get('Type', ''),
                    amount
                )

                # Create structured transaction
                transaction = {
                    'id': i + 1,  # Add unique ID
                    'transaction_date': self.parse_date(raw_transaction.get('Transaction Date', '')),
                    'post_date': self.parse_date(raw_transaction.get('Post Date', '')),
                    'description': self.clean_description(raw_transaction.get('Description', '')),
                    'category': raw_transaction.get('Category', '').strip(),
                    'amount': amount,
                    'memo': raw_transaction.get('Memo', '').strip(),
                    'type_info': type_info,
                    'metadata': {
                        'processed_at': datetime.now().isoformat(),
                        'original_row': i + 1
                    }
                }

                self.transactions.append(transaction)

            except Exception as e:
                print(f"Warning: Error processing row {i + 1}: {str(e)}")
                continue

        print(f"Successfully transformed {len(self.transactions)} transactions")
        return self.transactions

    def filter_transactions(self,
                            min_amount: Optional[float] = None,
                            max_amount: Optional[float] = None,
                            categories: Optional[List[str]] = None,
                            transaction_types: Optional[List[str]] = None,
                            date_range: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Filter transactions based on various criteria.

        Args:
            min_amount (float): Minimum absolute amount
            max_amount (float): Maximum absolute amount
            categories (List[str]): List of categories to include
            transaction_types (List[str]): List of transaction types to include ('debit', 'credit')
            date_range (tuple): Tuple of (start_date, end_date) in YYYY-MM-DD format

        Returns:
            List[Dict[str, Any]]: Filtered transactions
        """
        filtered = self.transactions.copy()

        if min_amount is not None:
            filtered = [t for t in filtered if t['type_info']['abs_amount'] >= min_amount]

        if max_amount is not None:
            filtered = [t for t in filtered if t['type_info']['abs_amount'] <= max_amount]

        if categories:
            categories_lower = [cat.lower() for cat in categories]
            filtered = [t for t in filtered if t['category'].lower() in categories_lower]

        if transaction_types:
            types_lower = [tt.lower() for tt in transaction_types]
            filtered = [t for t in filtered if t['type_info']['standardized_type'] in types_lower]

        if date_range:
            start_date, end_date = date_range
            filtered = [t for t in filtered
                        if start_date <= t['transaction_date'] <= end_date]

        print(f"Filtered to {len(filtered)} transactions")
        return filtered

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Generate summary statistics for the transactions.

        Returns:
            Dict[str, Any]: Summary statistics
        """
        if not self.transactions:
            return {}

        amounts = [t['amount'] for t in self.transactions]
        debits = [t['amount'] for t in self.transactions if t['type_info']['is_debit']]
        credits = [t['amount'] for t in self.transactions if t['type_info']['is_credit']]

        categories = {}
        for t in self.transactions:
            cat = t['category'] or 'Uncategorized'
            if cat not in categories:
                categories[cat] = {'count': 0, 'total_amount': 0}
            categories[cat]['count'] += 1
            categories[cat]['total_amount'] += t['amount']

        return {
            'total_transactions': len(self.transactions),
            'total_amount': sum(amounts),
            'average_amount': sum(amounts) / len(amounts),
            'debit_transactions': len(debits),
            'total_debits': sum(debits),
            'credit_transactions': len(credits),
            'total_credits': sum(credits),
            'date_range': {
                'earliest': min(t['transaction_date'] for t in self.transactions if t['transaction_date']),
                'latest': max(t['transaction_date'] for t in self.transactions if t['transaction_date'])
            },
            'categories': categories
        }

    def write_json(self,
                   include_summary: bool = True,
                   indent: int = 2,
                   transactions_to_write: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Write transactions to JSON file.

        Args:
            include_summary (bool): Whether to include summary statistics
            indent (int): JSON indentation level
            transactions_to_write (List[Dict]): Specific transactions to write (default: all)
        """
        try:
            data_to_write = transactions_to_write or self.transactions

            output_data = {
                'transactions': data_to_write
            }

            if include_summary:
                # Temporarily set transactions for summary calculation if needed
                original_transactions = self.transactions
                if transactions_to_write:
                    self.transactions = transactions_to_write

                output_data['summary'] = self.get_summary_statistics()

                # Restore original transactions
                self.transactions = original_transactions

            with open(self.json_file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(output_data, jsonfile, indent=indent, ensure_ascii=False)

            print(f"Successfully wrote {len(data_to_write)} transactions to {self.json_file_path}")

        except Exception as e:
            raise Exception(f"Error writing JSON file: {str(e)}")

    def parse_and_convert(self,
                          include_summary: bool = True,
                          filters: Optional[Dict[str, Any]] = None) -> None:
        """
        Complete pipeline: read CSV, transform, optionally filter, and write JSON.

        Args:
            include_summary (bool): Whether to include summary statistics in output
            filters (Dict): Filter criteria (min_amount, max_amount, categories, etc.)
        """
        # Read and transform
        self.read_csv()
        self.transform_transactions()

        # Apply filters if provided
        transactions_to_write = self.transactions
        if filters:
            transactions_to_write = self.filter_transactions(**filters)

        # Write JSON
        self.write_json(
            include_summary=include_summary,
            transactions_to_write=transactions_to_write if filters else None
        )

    def preview_transactions(self, num_transactions: int = 3) -> None:
        """
        Preview the first few transformed transactions.

        Args:
            num_transactions (int): Number of transactions to preview
        """
        print(f"Preview of first {min(num_transactions, len(self.transactions))} transactions:")
        for i, transaction in enumerate(self.transactions[:num_transactions]):
            print(f"Transaction {i + 1}:")
            print(json.dumps(transaction, indent=2))
            print("-" * 50)


# Example usage functions
def example_usage():
    """Example of how to use the TransactionCSVParser class."""

    # Create parser instance
    # parser = TransactionCSVParser('transactions.csv', 'transactions.json')
    parser = TransactionCSVParser(f'/Users/kenneth/Google Drive/2023Expense/2024/2024CHASE.CSV', 'transactions.json')

    # Option 1: Simple conversion with summary
    # parser.parse_and_convert()

    # Option 2: With filtering
    # filters = {
    #     'categories': ['Food & Drink', 'Transportation'],
    #     'min_amount': 10.0,  # Only transactions >= $10
    #     'transaction_types': ['debit']  # Only debit transactions
    # }
    #
    # parser.parse_and_convert(filters=filters)

    # Option 3: Step by step with preview
    parser.read_csv()
    parser.transform_transactions()
    parser.preview_transactions(2)

    # Get summary statistics
    summary = parser.get_summary_statistics()
    print("Summary Statistics:")
    print(json.dumps(summary, indent=2))

    # Write final JSON
    parser.write_json()


def example_filters():
    """Example filter configurations."""
    return {
        'food_transactions': {
            'categories': ['Food & Drink', 'Restaurants']
        },
        'large_debits': {
            'transaction_types': ['debit'],
            'min_amount': 100.0
        },
        'december_transactions': {
            'date_range': ('2024-12-01', '2024-12-31')
        }
    }


if __name__ == "__main__":
    example_usage()