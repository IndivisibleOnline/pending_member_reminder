from __future__ import print_function
import httplib2
import logging
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


class PendingMemberEmailHandler():

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # If modifying these scopes, delete your previously saved credentials
        # at ~/.credentials/gmail-python-quickstart.json
        # TODO: Check the value of this scope.  Was changed from quickstart
        self.scopes = 'https://www.googleapis.com/auth/gmail.readwrite'
        self.client_secret_file = 'pending_member_gmail_client_secret.json'
        self.application_name = 'IW Pending Member Reminder'

    def get_credentials(self):
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Ref: https://developers.google.com/gmail/api/quickstart/python

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'pending_member_reminder.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file, self.scopes)
            flow.user_agent = self.application_name
            #if flags:
            #    credentials = tools.run_flow(flow, store, flags)
            self.logger.info('Storing credentials to ' + credential_path)
        return credentials
