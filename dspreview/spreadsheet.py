from os.path import splitext, basename
from tempfile import TemporaryDirectory

import csv
import glob
import os
import subprocess

SPREADSHEET_TYPES = (
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.oasis.opendocument.spreadsheet-template',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
    'text/csv',)

def is_content_type_spreadsheet(content_type):
    return content_type in SPREADSHEET_TYPES

def convert_spreadsheet_to_csv(file_path, output_dir):
    cmd = 'ssconvert'
    exporter = 'Gnumeric_stf:stf_csv'
    output_files = output_dir + '/%s'
    subprocess.call([cmd, '--export-type', exporter, file_path, output_files, '-S'])
    return glob.glob(output_dir + '/*')

def csv_to_dict(file_path):
    data = []
    with open(file_path) as file:
        for row in csv.reader(file):
            data.append(row)
    return data


def get_spreadsheet_preview(params):
    sheets = {}
    # Work inside a temporary directory
    with TemporaryDirectory(prefix='gnumeric-') as output_dir:
        # Convert the entire spreadsheet and create one file per-sheet
        for sheet_file in convert_spreadsheet_to_csv(params['file_path'], output_dir):
            # Remove any extention from the file name
            sheet_name = basename(splitext(sheet_file)[0])
            # Save the sheet data
            sheets[sheet_name] = csv_to_dict(sheet_file)
    return sheets
