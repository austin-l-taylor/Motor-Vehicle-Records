from os import path

from docusign_esign import EnvelopesApi, EnvelopeDefinition, Document, Signer, CarbonCopy, SignHere, Tabs, Recipients, TemplateRole

from ...consts import demo_docs_path, pattern
from ...jwt_helpers import create_api_client
from datetime import datetime, timedelta
import os


class Eg002SigningViaEmailController:

    @classmethod
    def send_envelope(cls, args):
        """
        1. Create the envelope request object
        2. Send the envelope
        """

        envelope_args = args["envelope_args"]
        # 1. Create the envelope request object
        envelope_definition = cls.make_envelope(envelope_args)
        api_client = create_api_client(
            base_path=args["base_path"], access_token=args["access_token"])
        # 2. call Envelopes::create API method
        # Exceptions will be caught by the calling function
        envelopes_api = EnvelopesApi(api_client)
        results = envelopes_api.create_envelope(
            account_id=args["account_id"], envelope_definition=envelope_definition)
        envelope_id = results.envelope_id

        return {"envelope_id": envelope_id}

    @classmethod
    def make_envelope(cls, args):
        """
        Creates envelope
        args -- parameters for the envelope:
        signer_email, signer_name, signer_client_id
        returns an envelope definition
        """

        # Create the envelope definition
        envelope_definition = EnvelopeDefinition(
            status="sent",  # requests that the envelope be created and sent.
            template_id=args['template_id']
        )
        # Create template role elements to connect the signer and cc recipients
        # to the template
        signer = TemplateRole(
            email=args['signer_email'],
            name=args['signer_name'],
            role_name='signer')

        # Create a cc template role.
        # cc = TemplateRole(
        #     email=args['cc_email'],
        #     name=args['cc_name'],
        #     role_name='cc')

        # Add the TemplateRole objects to the envelope object
        envelope_definition.template_roles = [signer]
        return envelope_definition

    @classmethod
    def status_changes(cls, args, id_list):
        """
        Call the envelope status change method to list the         
        envelopes
        that have changed in the last 10 days
        """

        # Exceptions will be caught by the calling function
        api_client = create_api_client(
            base_path=args["base_path"], access_token=args["access_token"])
        api_client.host = args['base_path']
        api_client.set_default_header(
            "Authorization", "Bearer " + args['access_token'])
        envelope_api = EnvelopesApi(api_client)

        # The Envelopes::listStatusChanges method has many options
        # See https://developers.docusign.com/esign-rest-api/reference/Envelopes/Envelopes/listStatusChanges

        # The list status changes call requires at least a from_date OR
        # a set of envelopeIds. Here we filter using a from_date.
        # Here we set the from_date to filter envelopes for the last month
        # Use ISO 8601 date format
        # from_date = (datetime.utcnow() - timedelta(days=10)).isoformat()
        results = envelope_api.list_status_changes(
            args['account_id'], envelope_ids=','.join(id_list))

        return results

    @classmethod
    def download_documents(cls, args, envelope_id):
        api_client = create_api_client(
            base_path=args["base_path"], access_token=args["access_token"])
        envelope_api = EnvelopesApi(api_client)

        # The SDK always stores the received file as a temp file
        # Call the envelope get method
        # See https://developers.docusign.com/docs/esign-rest-api/reference/envelopes/envelopedocuments/get/

        temp_file_location = envelope_api.get_document(
            account_id=args["account_id"],
            document_id='combined',
            envelope_id=envelope_id)

        print(os.getcwd() + '\\' + envelope_id + '.pdf')
        os.rename(temp_file_location, os.getcwd() + '\\Mckenneys_Esign' +
                  '\\Signed Envelopes' + '\\' + envelope_id + '.pdf')
