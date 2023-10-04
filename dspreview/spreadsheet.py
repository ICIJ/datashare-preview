from os.path import splitext, basename
from tempfile import TemporaryDirectory
import csv
import glob
import subprocess
from typing import List, Dict

SPREADSHEET_TYPES = (
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'text/csv',)

SPREADSHEET_EXTS = ('.xls', '.xlsx', '.ods', '.csv', '.tsv')


def is_content_type_spreadsheet(content_type: str) -> bool:
    """
    Check if the given content type represents a spreadsheet.

    Args:
        content_type (str): The content type to check.

    Returns:
        bool: True if it's a spreadsheet content type, False otherwise.
    """
    return content_type in SPREADSHEET_TYPES


def is_ext_spreadsheet(ext: str) -> bool:
    """
    Check if the given file extension represents a spreadsheet.

    Args:
        ext (str): The file extension to check.

    Returns:
        bool: True if it's a spreadsheet file extension, False otherwise.
    """
    return ext in SPREADSHEET_EXTS


def convert_spreadsheet_to_csv(file_path: str, output_dir: str) -> List[str]:
    """
    Convert a spreadsheet file to CSV files and save them in the specified output directory.

    Args:
        file_path (str): The path to the spreadsheet file.
        output_dir (str): The directory where CSV files will be saved.

    Returns:
        List[str]: List of paths to the created CSV files.
    """
    cmd = 'ssconvert'
    exporter = 'Gnumeric_stf:stf_csv'
    output_files = output_dir + '/%s'
    subprocess.call([cmd, '--export-type', exporter,
                    file_path, output_files, '-S'])
    return glob.glob(output_dir + '/*')


def csv_to_dict(file_path: str) -> List[List[str]]:
    """
    Read a CSV file and return its content as a list of lists.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        List[List[str]]: List of lists representing the CSV data.
    """
    data = []
    with open(file_path) as file:
        for row in csv.reader(file):
            data.append(row)
    return data


def get_spreadsheet_preview(file_path: str) -> Dict[str, List[List[str]]]:
    """
    Convert a spreadsheet to CSV files and return the data as a dictionary of sheets.

    Args:
        file_path (str): The path to the spreadsheet file.

    Returns:
        Dict[str, List[List[str]]]: A dictionary where keys are sheet names and values are CSV data as lists of lists.
    """
    sheets = {}
    # Work inside a temporary directory
    with TemporaryDirectory(prefix='gnumeric-') as output_dir:
        # Convert the entire spreadsheet and create one file per-sheet
        for sheet_file in convert_spreadsheet_to_csv(file_path, output_dir):
            # Remove any extension from the file name
            sheet_name = basename(splitext(sheet_file)[0])
            # Avoid using the file name as sheet name
            sheet_name = 'main' if sheet_name == basename(
                file_path) else sheet_name
            # Save the sheet data
            sheets[sheet_name] = csv_to_dict(sheet_file)
    return sheets
