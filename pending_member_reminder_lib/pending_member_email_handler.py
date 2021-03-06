"""

pending_member_email_handler.py
===========

Desc     :  Manages content creation and interaction with Gmail to send the email(s) as appropriate


"""

from __future__ import print_function
import base64
from email.mime.text import MIMEText

import httplib2
import logging
import os
import sys

from apiclient import discovery
from googleapiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


class PendingMemberEmailHandler():

    def __init__(self, recipient_list, pending_user_list, mail_credentials, input_args):
        """
        Constructor for email handler object.
        :param recipient_list: List of recipients (list of string email addresses) to whom we should send reminders
        :param pending_user_list: List of tuples (id, name, email) who are are defined as pending users
        :param mail_credentials: Dict of relevant credential information for connection / sending
        :return:
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.input_args = input_args

        self.scopes = mail_credentials['scopes']
        self.client_secret_file = mail_credentials['client_secret_file']
        self.application_name = mail_credentials['application_name']
        self.sender_email = mail_credentials['sender_email']

        self.logger.debug('SCOPES: [%s]' % self.scopes)
        self.logger.debug('CLIENT_SECRET_FILE: [%s]' % self.client_secret_file)
        self.logger.debug('APPLICATION_NAME: [%s]' % self.application_name)
        self.logger.debug('SENDER: [%s]' % self.sender_email)

        self.recipient_list = recipient_list
        if type(recipient_list) == str:
            self.recipient_list = [recipient_list]

        self.pending_user_list = pending_user_list
        if type(pending_user_list) == str:
            self.pending_user_list = [pending_user_list]

        self.logger.debug('Recipient list is size %s' % len(self.recipient_list))
        self.logger.debug('Pending user list is size %s' % len(self.pending_user_list))

        self.credentials = self.get_credentials()
        http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)

    @staticmethod
    def _get_message_subject_line(num_days):
        """
        Determine severity term we want to use for the outgoing message
        (based on how long clients have been waiting in queue)

        :param num_days: Number of days which was used as basis for pending users query
        :return: String with either 'URGENT' or 'NOTICE
        """
        if num_days > 7:
            severity_term = 'URGENT'
        else:
            severity_term = 'NOTICE'

        return '%s: IW members have been waiting at least %d days for team assignment' % (severity_term, num_days)

    def _create_reminder_content(self, num_days):
        """
        Returns the body of an email message to be sent

        :param num_days: Minimum number of days pending users have been waiting
        :return: String, properly formatted body of email
        """

        email_content = """Dear IW Admins,

There are currently %d people who have been waiting at least %d days to be assigned to a local Indivisible Westchester chapter:

%s

Please make sure these individuals are assigned as soon as possible!  Regards - tech@indivisiblewestchester.org


Note: This email was auto-generated by %s.  Remove from cron (or equivalent) to cease.  Contact tech@indivisiblewestchester.org to be removed from list.
""" % (len(self.pending_user_list), num_days, '\n'.join([p[1] + ' (' + p[2] + ')' for p in self.pending_user_list]), sys.argv[0])

        return email_content

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
            credentials = tools.run_flow(flow, store, self.input_args)
            self.logger.info('Storing credentials to ' + credential_path)
        return credentials

    def _create_message_object(self, num_days):
        """
        Creates the actual message (MIMEText object) for an outgoing email
        :param num_days: Number of days which was used as basis for pending users query
        :return: base64 encoded MIMEText object with body and relevant header information (to/from/subject)
        """
        message_content = self._create_reminder_content(num_days)
        self.logger.debug(message_content)

        self.logger.debug('Preparing email for sending')
        mime_message = MIMEText(message_content)
        mime_message['to'] = ','.join(self.recipient_list)  # TODO: Check that giving this a list of string emails actually works
        mime_message['from'] = self.sender_email
        mime_message['subject'] = self._get_message_subject_line(num_days)

        self.logger.debug(mime_message.as_string())


        return {'raw': base64.urlsafe_b64encode(mime_message.as_string())}

    def send_reminders(self, num_days):
        """
        Format and send the outgoing message(s) to the intended recipients
        :param num_days: Number of days the pending users have been waiting for an assignment
        :return: True if we have successfully sent the emails, False else
        """

        if not self.recipient_list:
            errmsg = 'No recipient list associated with %s - aborting send' % self.__class__.__name__
            self.logger.error(errmsg)
            raise RuntimeError(errmsg)

        if not self.pending_user_list:
            errmsg = 'No pending user list associated with %s - aborting send' % self.__class__.__name__
            self.logger.error(errmsg)
            raise RuntimeError(errmsg)

        # TODO: Actually execute the email send protocol :)
        mime_message = self._create_message_object(num_days)
        try:
            message = (self.service.users().messages().send(userId='me', body=mime_message)
                       .execute())
            self.logger.info('Message Id: %s' % message['id'])
            return message
        except errors.HttpError, error:
            print('An error occurred: %s' % error)





