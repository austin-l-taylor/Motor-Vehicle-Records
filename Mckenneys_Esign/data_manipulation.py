import csv
import pandas as pd
import os
from os import path

# ---PANDAS AND CSV DATA MANIPULATION TESTING ENVIRONMENT---#


def add_envelopeID_rows(envelope_id, index):

    df = pd.read_csv('SPdump.csv')

    # Checks if the Envelope ID column Exists and adds the envelope Ids to each row but only if row is null
    if 'Envelope ID' in df.columns:

        print("Envelope ID column already exists")

    # Creates the Envelope Column
    else:
        df['Envelope ID'] = pd.Series(dtype='object')
        df.to_csv('SPdump.csv', index=False)

    # adds the envelpe id at the index of the csv
    df.at[index, 'Envelope ID'] = envelope_id
    df.to_csv('SPdump.csv', index=False)


def change_name_to_email():
    csv_path = "C:\Docusign_Esignature_Test\Mckenneys_Esign\Envelopes_Sent.csv"
    df = pd.read_csv(csv_path)

    df['Requestor'] = df['Requestor'].astype(str)
    df['Requestor'] = df['Requestor'].str.lower()
    df['Requestor'] = df['Requestor'].apply(
        lambda x: '.' .join(x.split()) + "@mckenneys.com")

    for value in df['Requestor']:
        print(value)


def create_mvr_rows():

    spdump_path = "C:/Docusign_Esignature_Test/Mckenneys_Esign/SPdump.csv"

    # Reads the csv
    combined_column = pd.read_csv(spdump_path)
    arrange_column = pd.read_csv(spdump_path)

    # Concatenates to a string and combines to a single column
    combined_column['Employee Name'] = combined_column['FirstName'].astype(
        str) + combined_column['LastName'].astype(str)

    # Dropping columns not in MVR smartsheet
    arrange_column = arrange_column.drop('FirstName', axis=1)
    arrange_column = arrange_column.drop('LastName', axis=1)
    arrange_column = arrange_column.drop('VehicleAssignment', axis=1)
    arrange_column = arrange_column.drop('VehicleNumber', axis=1)
    arrange_column = arrange_column.drop('Email', axis=1)

    # Renaming columns
    arrange_column = arrange_column.rename(
        columns={'EmpID': 'Employee ID', 'SupervisorName': 'Requestor', 'VehicleAssignmentStatus': 'Status'})

    # Concats, shifts, and udpates columns
    updated = pd.concat(
        [combined_column['Employee Name'], arrange_column], axis=1)
    updated = updated.reindex(
        columns=['Employee Name', 'Employee ID', 'Requestor', 'Status', 'Envelope ID'])
    updated.loc[:, 'Status'] = "Awaiting Signature"
    updated['Requestor'] = updated['Requestor'].astype(str)
    updated['Requestor'] = updated['Requestor'].str.lower()
    updated['Requestor'] = updated['Requestor'].apply(
        lambda x: '.' .join(x.split()) + "@mckenneys.com")
    updated.to_csv('Envelopes_Sent.csv', index=False)


def get_envelope_ids():

    mvr_smartsheet_path = "C:/Docusign_Esignature_Test/Mckenneys_Esign/MVR_smartsheet.csv"
    check_status = pd.read_csv(mvr_smartsheet_path)

    awaiting_signature = check_status[check_status['Status']
                                      == 'Awaiting Signature']

    envelope_ids = awaiting_signature['Envelope ID'].tolist()

    envelope_ids = [
        null_value for null_value in envelope_ids if str(null_value) != 'nan']

    return envelope_ids


def check_spdump_status():

    df = pd.read_csv('SPdump.csv')

    if 'Status' in df.columns:
        print('status column exists')
    else:
        df['Status'] = pd.Series(dtype='object')

    df.at[0, 'Status'] = 'sent'

    df.to_csv('SPdump.csv', index=False)


def get_row_length():

    if path.exists(os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv') == True:
        with open(os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv', 'r') as file:
            reader = csv.reader(file)
            data = list(reader)

        num_rows = len(data) - 1

        return num_rows

    else:
        return 0


# add_envelopeID_rows()
# create_mvr_rows()
# add_envelopeID_rows()
# check_spdump_status()
get_row_length()
# change_name_to_email()
