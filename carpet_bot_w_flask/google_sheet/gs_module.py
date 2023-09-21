# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import os
import pickle
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from config_data.config import spreadsheet_id, credentials_path


class GoogleSheet:
    """Class to handle Google Sheets operations."""
    SPREADSHEET_ID = spreadsheet_id
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    TOKEN_PATH = 'token.pickle'
    CREDENTIALS_PATH = credentials_path

    def __init__(self):
        """Initializes the GoogleSheet class and authenticate the service."""
        self.creds = self._load_credentials()
        self._ensure_service_is_authenticated()

    def _ensure_service_is_authenticated(self):
        """Ensure service is authenticated and update if needed."""
        if not self.creds or not self.creds.valid:
            self.creds = self._refresh_or_create_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)

    def _load_credentials(self):
        """Load credentials from pickle file if it exists."""
        if os.path.exists(self.TOKEN_PATH):
            with open(self.TOKEN_PATH, 'rb') as token:
                return pickle.load(token)
        return None

    def _refresh_or_create_credentials(self):
        """Refresh existing or create new credentials."""
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.CREDENTIALS_PATH, self.SCOPES
                )
            self.creds = flow.run_local_server(port=0)
        with open(self.TOKEN_PATH, 'wb') as token:
            pickle.dump(self.creds, token)
        return self.creds

    def execute(self, method, *args, **kwargs):
        """Execute a method on the service."""
        try:
            return method(*args, **kwargs).execute()
        except Exception as general_error:
            print(f"General error: {general_error}")
            return None

    def get_column_indexes_from_range(self, range_name):
        """Extract start and end column indexes from a range."""
        start_column_letter, end_column_letter = re.findall(r"[A-Z]+",
                                                            range_name)
        return (ord(start_column_letter) - ord('A'),
                ord(end_column_letter) - ord('A') + 1)

    def get_next_order_id(self, sheet_name):
        range_name = f'{sheet_name}!A2:A'
        # pylint: disable=no-member
        result = self.execute(
            self.service.spreadsheets().values().get,
            spreadsheetId=self.SPREADSHEET_ID,
            range=range_name
        )
        values = result.get('values', [])
        return int(values[-1][0]) + 1 if values else 1

    def get_next_order_row(self, sheet_name):
        range_name = f'{sheet_name}!A2:A'
        # pylint: disable=no-member
        result = self.execute(
            self.service.spreadsheets().values().get,
            spreadsheetId=self.SPREADSHEET_ID,
            range=range_name
        )
        values = result.get('values', [])
        return len(values) + 2 if values else 2

    def write_order(self, equipment_details, sheet_name):
        """Add equipment details to the Google Sheet."""
        headers = self._fetch_headers(sheet_name)
        values = self._prepare_values(equipment_details, headers)
        range_name = self._construct_range_name(sheet_name, headers)
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': [{'range': range_name, 'values': values}]
        }
        # pylint: disable=no-member
        self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=self.SPREADSHEET_ID, body=body).execute()
        sheet_id = self.get_sheet_id_by_name(sheet_name)
        self.format_cells(range_name, sheet_id)

    def _fetch_headers(self, sheet_name):
        headers_range = f'{sheet_name}!A1:J1'
        # pylint: disable=no-member
        headers_response = self.execute(
            self.service.spreadsheets().values().get,
            spreadsheetId=self.SPREADSHEET_ID,
            range=headers_range
        )
        return headers_response.get('values', [])[0]

    def _prepare_values(self, equipment_details, headers):
        values = [[]]
        for header in headers:
            print(header)
            value = equipment_details.get(header, "")
            # if header in ("Номер телефону", "phone"):
            #     print(value)
            #     value = value.rjust(10, '0')
            values[0].append(value)
        return values

    def _construct_range_name(self, sheet_name, headers):
        num_columns = len(headers)
        start_column = 'A'
        end_column = chr(ord(start_column) + num_columns - 1)
        row_number = self.get_next_order_row(sheet_name=sheet_name)
        return (f'{sheet_name}!{start_column}{row_number}:'
                f'{end_column}{row_number}')

    def fetch_data(self, sheet_name):
        columns = ['A', 'B', 'C', 'D']
        keys = ['name', 'price', 'description', 'image_url']

        # Fetch data from sheets
        data = {}
        for col, key in zip(columns, keys):
            range_name = f"{sheet_name}!{col}2:{col}"
            # pylint: disable=no-member
            result = self.execute(
                self.service.spreadsheets().values().get,
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name
            ).get('values', [])
            data[key] = [item[0] if len(item) > 0 else None for item in result]

        # Create a dictionary of products
        products = {}
        for i in range(len(data['name'])):
            price = None
            if i < len(data['price']):
                price = data['price'][i]

            description = None
            if i < len(data['description']):
                description = data['description'][i]

            image_url = None
            if i < len(data['image_url']):
                image_url = data['image_url'][i]

            product_info = {
                'price': price,
                'description': description,
                'image_url': image_url
            }

            products[data['name'][i]] = product_info

        return products

    # for sub_sheet
    def get_sheet_id_by_name(self, sheet_name):
        """Отримати ID листа на основі його назви.

        :param sheet_name: Назва листа.
        :return: ID листа.
        """
        try:
            # отримання інформації про всі листи в таблиці
            sheets_service = getattr(self.service, "spreadsheets")
            sheets_info = sheets_service().get(
                spreadsheetId=self.SPREADSHEET_ID
            ).execute()

            # Перевірка всіх листів в отриманій таблиці
            for sheet in sheets_info['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']

            # Якщо лист з такою назвою не знайдено, повертаємо None
            print(f"No sheet found with the name: {sheet_name}")
            return None

        except Exception as sheet_id_error:
            print(f"Error getting sheet ID for name '{sheet_name}': "
                  f"{sheet_id_error}")
            return None

    def format_cells(self, range_name, sheet_id):
        """Format cells with borders and centered alignment."""
        start_column_index, end_column_index = (
            self.get_column_indexes_from_range(range_name))
        start_row_index = int(
            re.search(r'\d+', range_name.split(':')[0]).group()) - 1
        end_row_index = start_row_index + 1

        border_style = {'style': 'SOLID', 'width': 1}
        requests = [
            {
                'updateBorders': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': start_row_index,
                        'endRowIndex': end_row_index,
                        'startColumnIndex': start_column_index,
                        'endColumnIndex': end_column_index
                    },
                    'top': border_style,
                    'bottom': border_style,
                    'left': border_style,
                    'right': border_style,
                    'innerHorizontal': border_style,
                    'innerVertical': border_style
                }
            },
            {
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': start_row_index,
                        'endRowIndex': end_row_index,
                        'startColumnIndex': start_column_index,
                        'endColumnIndex': end_column_index
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'horizontalAlignment': 'CENTER',
                            'verticalAlignment': 'MIDDLE'
                        }
                    },
                    'fields': (
                        'userEnteredFormat(horizontalAlignment,'
                        'verticalAlignment)'
                        )
                }
            }
        ]

        body = {'requests': requests}
        print("Calling spreadsheets method...")
        # pylint: disable=no-member
        result = self.execute(
            self.service.spreadsheets().batchUpdate,
            spreadsheetId=self.SPREADSHEET_ID,
            body=body
        )
        print("Result:", result)

    def fetch_carpet_images(self, sheet_name):
        columns = ['A', 'B', 'C']
        levels = ['simple', 'middle', 'hard']

        # Fetch data from sheets
        data = {}
        for col, level in zip(columns, levels):
            range_name = f"{sheet_name}!{col}2:{col}"
            # pylint: disable=no-member
            result = self.execute(
                self.service.spreadsheets().values().get,
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name
            ).get('values', [])
            data[level] = [item[0] for item in result if item]

        return data
