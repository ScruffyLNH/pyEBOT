import gspread  # Module needed for google sheets.
import csv
import string
import json
from oauth2client.service_account import ServiceAccountCredentials
# from pprint import pprint  # Print pretty messages.

# Get scope for google sheets.
scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"]

# Credentials file from Google Cloud Console. This is generated by Google Drive
# API and allows Python to connect to your Google Drive.
# Make sure to add this file to gitignore.
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "creds.json", scope
)

# Make a Google Sheets client and connect it to your Google Drive.
client = gspread.authorize(creds)

"""
sheet = client.open("pyEBOT test sheet").sheet1


data = sheet.get_all_records()

pprint(data)
"""
# TODO: Do some error handling to prevent crashing if sheet names change.
# Get sheetnames and keys from json file.
with open("gsheetsConfig.json", "r") as f:
    sheetsConfig = json.load(f)
    f.close()

spreadSheet = client.open(sheetsConfig['eventSheet'])
sheet = spreadSheet.worksheet('Discord Parsed Data')

daymarSpreadSheet = client.open_by_key(sheetsConfig['daymarSpreadSheetKey'])
daymarSheet = daymarSpreadSheet.worksheet('SECURITY')
daymarOverviewSheet = daymarSpreadSheet.worksheet('ALL')


# Functions
def numToA(n, b=string.ascii_uppercase):
    """Converts number to column letter notation. (Zero indexed.)

    :param n: Number to convert
    :type n: int
    :param b: Letters to convert to. Defaults to string.ascii_uppercase
    :type b: string constant, optional
    :return: The column letter notation of the input.
    :rtype: str
    """

    d, m = divmod(n, len(b))
    return numToA(d-1, b) + b[m] if d else b[m]


def getCell(rowIndex, colIndex, daymar=False):
    if daymar:
        cell = daymarSheet.cell(rowIndex, colIndex)
    else:
        cell = sheet.cell(rowIndex, colIndex)
    return cell.value


def setCell(rowIndex, colIndex, value, daymar=False):
    if daymar:
        daymarSheet.update_cell(rowIndex, colIndex, value)
    else:
        sheet.update_cell(rowIndex, colIndex, value)


def setRange(startIndex, endIndex, data, daymar=False):

    # Convert indices to A1 notation.
    start = numToA(startIndex[1]) + str(startIndex[0] + 1)
    end = numToA(endIndex[1]) + str(endIndex[0] + 1)
    a1Range = ':'.join([start, end])

    if daymar:
        daymarSheet.update(a1Range, data)
    else:
        sheet.update(a1Range, data)


def getAll(daymar=False, daymarOverview=False):

    if daymar:
        return daymarSheet.get_all_records()
    elif daymarOverview:
        return daymarOverviewSheet.get_all_records()
    else:
        return sheet.get_all_records()


def getAllValues(daymar=False, daymarOverview=False):

    if daymar:
        return daymarSheet.get_all_values()
    elif daymarOverview:
        return daymarOverviewSheet.get_all_values()
    else:
        return sheet.get_all_values()


def getCol(index, daymar=False):

    if daymar:
        return daymarSheet.col_values(index)
    else:
        return sheet.col_values(index)


def getRow(rowNum, daymar=False):

    if daymar:
        data = daymarSheet.row_values(rowNum)
    else:
        data = sheet.row_values(rowNum)
    return data


def deleteRows(startIndex, rowNum=1, daymar=False):

    if rowNum < 1:
        return

    if daymar:
        daymarSheet.delete_dimension(
            'ROWS', startIndex, startIndex + rowNum - 1
        )
    else:
        sheet.delete_dimension('ROWS', startIndex, startIndex + rowNum - 1)


def exportCsv(fileName):

    with open(fileName, 'w', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerows(daymarOverviewSheet.get_all_values())

        return fp


# This must run periodically to avoid loosing authentication. Timeout is 1hr.
def refreshAuth():

    global client
    global spreadSheet
    global sheet
    global daymarSpreadSheet
    global daymarSheet
    global daymarOverviewSheet

    client = gspread.authorize(creds)

    # TODO Make a gsheets config file for sheet names and keys and track
    # sheets.py
    with open("gsheetsConfig.json", "r") as f:
        sheetsConfig = json.load(f)
        f.close()

    spreadSheet = client.open(sheetsConfig['eventSheet'])
    sheet = spreadSheet.worksheet('Discord Parsed Data')

    daymarSpreadSheet = client.open_by_key(
        sheetsConfig['daymarSpreadSheetKey']
    )
    daymarSheet = daymarSpreadSheet.worksheet('SECURITY')
    daymarOverviewSheet = daymarSpreadSheet.worksheet('ALL')


# TODO: Encapsulate this code within a class to make it compatible with sphinx
# documentation.
