import csv
import logging
import requests
from urllib.parse import urlparse, parse_qs


class GoogleSheetsTable:
    """
    GoogleSheetsTable provides a drop-in replacement for pyairtable.Table
    using Google Sheets CSV export. Maintains identical interface and data structure.
    """

    def __init__(self, sheet_url: str):
        """
        Initialize with Google Sheets URL.

        Args:
            sheet_url: Public Google Sheets URL (will be converted to CSV export format)
        """
        self.sheet_url = sheet_url
        self.csv_url = self._convert_to_csv_url(sheet_url)

    def _convert_to_csv_url(self, sheet_url: str) -> str:
        """
        Convert Google Sheets URL to CSV export format.

        Handles URLs like:
        - https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=0
        - https://docs.google.com/spreadsheets/d/SHEET_ID/edit?usp=sharing

        Returns CSV export URL:
        - https://docs.google.com/spreadsheets/d/SHEET_ID/export?format=csv&gid=0
        """
        try:
            # Extract sheet ID from URL
            if "/spreadsheets/d/" in sheet_url:
                sheet_id = sheet_url.split("/spreadsheets/d/")[1].split("/")[0]

                # Extract gid if present
                gid = "0"  # default
                if "#gid=" in sheet_url:
                    gid = sheet_url.split("#gid=")[1].split("&")[0]
                elif "gid=" in sheet_url:
                    parsed = urlparse(sheet_url)
                    query_params = parse_qs(parsed.query)
                    gid = query_params.get('gid', ['0'])[0]

                return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
            else:
                # Assume it's already a CSV URL or direct URL
                return sheet_url
        except Exception as error:
            logging.warning(f"Failed to convert Google Sheets URL, using as-is: {error}")
            return sheet_url

    def all(self) -> list[dict]:
        """
        Fetch all records from Google Sheets.

        Returns identical structure to pyairtable.Table.all():
        [{"id": "row_1", "fields": {"Name": "...", "Price": 123, "Message": "...", "isEnabled": True}}]
        """
        logging.info("Fetching data from Google Sheets...")

        try:
            # Fetch CSV data
            response = requests.get(self.csv_url, timeout=30)
            response.raise_for_status()

            # Parse CSV data
            csv_data = csv.DictReader(response.text.splitlines())
            records = []

            for row_num, row in enumerate(csv_data, 1):
                # Convert to exact pyairtable format
                record = {
                    "id": f"row_{row_num}",  # Simple ID generation
                    "fields": {
                        "Name": self._convert_string(row.get("Name")),
                        "Price": self._convert_price(row.get("Price")),
                        "Message": self._convert_string(row.get("Message")),
                        "isEnabled": self._convert_boolean(row.get("isEnabled"))
                    }
                }
                records.append(record)

            logging.info(f"Successfully fetched {len(records)} records from Google Sheets")
            return records

        except requests.exceptions.RequestException as error:
            logging.error(f"Network error fetching Google Sheets data: {error}")
            return []  # Graceful degradation
        except Exception as error:
            logging.error(f"Failed to parse Google Sheets data: {error}")
            return []  # Graceful degradation

    def _convert_string(self, value: str) -> str | None:
        """
        Convert string value, handling None and empty strings.
        """
        if not value or value.strip() == "":
            return None
        return value.strip()

    def _convert_price(self, value: str) -> int | None:
        """
        Convert price value to integer, handling None and invalid values.
        """
        if not value or value.strip() == "":
            return None
        try:
            # Handle decimal inputs by converting to float first, then int
            return int(float(value.strip()))
        except (ValueError, TypeError):
            logging.warning(f"Invalid price value: '{value}', returning None")
            return None

    def _convert_boolean(self, value: str) -> bool | None:
        """
        Convert boolean value from various string representations.
        """
        if not value:
            return None

        value_lower = str(value).lower().strip()

        # True values
        if value_lower in ["true", "1", "yes", "on", "enabled"]:
            return True
        # False values
        elif value_lower in ["false", "0", "no", "off", "disabled"]:
            return False
        else:
            logging.warning(f"Invalid boolean value: '{value}', returning None")
            return None