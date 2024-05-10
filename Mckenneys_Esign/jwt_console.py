from os import path
import os
import sys
import subprocess
import csv
import pandas as pd

from docusign_esign import ApiClient
from docusign_esign.client.api_exception import ApiException
from app.jwt_helpers import get_jwt_token, get_private_key
from app.eSignature.examples.eg002_signing_via_email import Eg002SigningViaEmailController
from app.jwt_config import DS_JWT
from keeper_helper import get_secrets

# pip install DocuSign SDK
subprocess.check_call([sys.executable, '-m', 'pip',
                      'install', 'docusign_esign'])

SCOPES = [
    "signature", "impersonation"
]


def get_consent_url():
    url_scopes = "+".join(SCOPES)

    # Construct consent URL
    redirect_uri = "https://developers.docusign.com/platform/auth/consent"
    consent_url = f"https://{DS_JWT['authorization_server']}/oauth/auth?response_type=code&" \
                  f"scope={url_scopes}&client_id={DS_JWT['ds_client_id']}&redirect_uri={redirect_uri}"

    return consent_url


def get_token(private_key, api_client):
    # Call request_jwt_user_token method
    token_response = get_jwt_token(
        private_key, SCOPES, DS_JWT["authorization_server"], DS_JWT["ds_client_id"], DS_JWT["ds_impersonated_user_id"])
    access_token = token_response.access_token

    # Save API account ID
    user_info = api_client.get_user_info(access_token)
    accounts = user_info.get_accounts()

    return {"access_token": access_token, "api_account_id": DS_JWT["api_account_id"], "base_path": DS_JWT["base_path"]}

# Gets envelope arguments


def get_envelope_args(signer_email, signer_name, template_id):
    envelope_args = {
        "signer_email": signer_email,
        "signer_name": signer_name,
        "status": "sent",
        "template_id": template_id,
    }

    return envelope_args

# Gets authorization arguments


def get_args(api_account_id, access_token, base_path, envelope_args=None):
    args = {
        "account_id": api_account_id,
        "base_path": base_path,
        "access_token": access_token,
        "envelope_args": envelope_args
    }

    return args

# Creates an envelope.


def create_envelope(args):
    result = Eg002SigningViaEmailController.send_envelope(args)

    envelope_id = result['envelope_id']

    print(f"Your envelope has been sent. {envelope_id}")

    return envelope_id


def create_all_envelopes(jwt_values, template_id):
    index = 0

    # Iterates through the csv and saves the data to a dictionary then resets the dictionary to the next index
    with open(os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv', mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:

            # Define envelope args
            first_name = row['FirstName']
            email = row['Email']

            if index < get_row_length():
                # Build args objects
                envelope_args = get_envelope_args(email, first_name, template_id)
                args = get_args(
                    jwt_values["api_account_id"], jwt_values["access_token"], jwt_values["base_path"], envelope_args)

                # pass in envelope id to add evnvelopeIDrows function then add to csv
                envelope_id = create_envelope(args)
                add_envelopeID_rows(envelope_id, index)

                print(f"data for envelope #{index+1} is: {envelope_args}")

                status = envelope_args['status']

                print(f"envelope status is: {status}")
                print(f"current index is: {index}")

                if status == 'sent':
                    check_spdump_status(index, status)
                else:
                    check_spdump_status(index, status='failed send')

                index += 1

            else:
                break

# Checks all the statuses of each envelope and downloads envelope attachments.


def check_statuses(args):
    signed_enevlope_list = []
    id_list = get_envelope_ids()

    print(f"All envelope Id's with a status Awaiting Signature: {id_list}")
    envelope_statuses = Eg002SigningViaEmailController.status_changes(
        args, id_list)

    # Filters dictionary down to all "Completed" forms status and if completed then call download_pdf
    for envelope in envelope_statuses.envelopes:

        if envelope.status == 'completed':

            print(f"complete satus envelope id is: {envelope.envelope_id}")
            envelope_id = envelope.envelope_id
            signed_enevlope_list.append(envelope_id)
            Eg002SigningViaEmailController.download_documents(
                args, envelope_id)

        else:

            print("Envelope status is not complete")

        if not signed_enevlope_list:
            print("completed signed envelopes list is empty")

        else:

            signed_envelopes = pd.DataFrame()
            signed_envelopes['Envelope ID'] = pd.Series(dtype='object')
            signed_envelopes['Envelope ID'] = signed_enevlope_list
            signed_envelopes.to_csv(
                os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\signed_envelopes.csv', index=False)

    print(f"List of signed envelope ids: {signed_enevlope_list}")
    return envelope_statuses

# Checks the status of the envelope ids.


def check_all_statuses(jwt_values):
    try:
        args = get_args(jwt_values["api_account_id"],
                        jwt_values["access_token"], jwt_values["base_path"])
        check_statuses(args)

    except ApiException as err:
        body = err.body.decode('utf8')

        if "consent_required" in body:
            consent_url = get_consent_url()
            print(
                "Open the following URL in your browser to grant consent to the application:")
            print(consent_url)
            consent_granted = input(
                "Consent granted? Select one of the following: \n 1)Yes \n 2)No \n")
            # Calls the check status function.
            if consent_granted == "1":
                check_statuses(args)
            else:
                sys.exit("Please grant consent")
        else:
            raise

# Adds the envelope ID column and all envelope ids.


def add_envelopeID_rows(envelope_id, index):
    df = pd.read_csv(os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv')

    # Checks if the Envelope ID column Exists and adds the envelope Ids to each row but only if row is null
    if 'Envelope ID' in df.columns:

        print("Envelope ID column already exists")

    # Creates the Envelope Column
    else:
        df['Envelope ID'] = pd.Series(dtype='object')
        df.to_csv(os.getcwd() +
                  '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv', index=False)

    # adds the envelpe id at the index of the csv
    df.at[index, 'Envelope ID'] = envelope_id
    df.to_csv(os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv', index=False)


def create_mvr_rows():
    spdump_path = os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv'

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
    updated['Requestor'] = updated['Requestor'].astype(str)
    updated['Requestor'] = updated['Requestor'].str.lower()
    updated['Requestor'] = updated['Requestor'].apply(
        lambda x: '.' .join(x.split()) + "@mckenneys.com")
    updated.loc[:, 'Status'] = "Awaiting Signature"
    updated.to_csv(
        os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\envelopes_sent.csv', index=False)

# Returns a list of Envelope IDs from MVR Smartsheet with an "Awaiting Signature" status.


def get_envelope_ids():
    mvr_smartsheet_path = os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\MVR_smartsheet.csv'
    check_status = pd.read_csv(mvr_smartsheet_path)

    num_of_awaiting_signaturesre = check_status[check_status['Status']
                                                == 'Awaiting Signature']

    envelope_ids = num_of_awaiting_signaturesre['Envelope ID'].tolist()

    envelope_ids = [
        null_value for null_value in envelope_ids if str(null_value) != 'nan']

    return envelope_ids

# Returns the number of rows in the csv.


def get_row_length():
    if path.exists(os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv') == True:
        with open(os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv', 'r') as file:
            reader = csv.reader(file)
            data = list(reader)

        num_rows = len(data) - 1

        return num_rows

    else:
        return 0

# Adds the Envelope Status column in MVR and adds the current status of every envelope.


def check_spdump_status(index, status):
    df = pd.read_csv(os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv')

    if 'Envelope Status' in df.columns:
        print('status column exists')
    else:
        df['Envelope Status'] = pd.Series(dtype='object')

    df.at[index, 'Envelope Status'] = status
    df.to_csv(os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv', index=False)


def main():
    # Initiates api client
    api_client = ApiClient()
    api_client.set_base_path(DS_JWT["authorization_server"])
    api_client.set_oauth_host_name(DS_JWT["authorization_server"])

    # Fetch secret from the Keeper vault
    secret = get_secrets(["2j7Y-WzNtVBWGmAs2hRcMw"])[0]
    template_id = secret.custom_field("Template ID", field_type=None, single=True, value=None)
    private_key = secret.field('keyPair', single=True)["privateKey"]

    # Build auth data
    # idk why its encoding and decoding, but docusign said to do so
    private_key = private_key.encode("ascii").decode("utf-8")
    jwt_values = get_token(private_key, api_client)

    num_rows = get_row_length()
    num_of_awaiting_signatures = get_envelope_ids()

    # ---SENDS OUT ENVELOPES AND CHECKS ENVELOPE STATUSES FROM MVR---#

    # checks if there is any data in SPdump to create new envelopes and updates status
    sp_dump_path = os.getcwd() + '\\Mckenneys_Esign\\CSV_Folder\\SPdump.csv'

    if os.path.exists(sp_dump_path):

        print(f"There are {num_rows} rows to run")

        # creates all envelopes in SPdump.csv
        create_all_envelopes(jwt_values, template_id)

        # create csv to match MVR smartsheet with envelope id data
        create_mvr_rows()

        # checks the status of every envelope with an "Awaiting Signature" attribute from the MVR Smartsheet csv
        print("Checking number of Awaiting Signature statuses.")
        if len(num_of_awaiting_signatures) != 0:
            check_all_statuses(jwt_values)
        else:
            print("no statuses to check")

    # ---DOES NOT SEND OUT ENVELOPES ONLY CHECKS STATUSES FROM MVR---#

    # checks if the envelope ids is not equal to 0
    if len(num_of_awaiting_signatures) != 0:

        print(f"Statuses to check is: {len(num_of_awaiting_signatures)}.")
        # checks the status of every envelope with an "Awaiting Signature" attribute from the MVR Smartsheet csv and downloads all signed forms
        check_all_statuses(jwt_values)

    # outputs message only if there are no statuses to check and no envelopes to be sent out.
    else:
        print("No envelopes to send and no statuses to check")


main()
