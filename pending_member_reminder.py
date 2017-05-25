"""

pending_member_reminder.py
===========

Desc     :  Task to contact IW administrators when there are website members who have been waiting
            too long for group assignment


"""

import argparse
import datetime
import json
import logging

from pending_member_reminder_lib.pending_member_db_accessor import PendingMemberDbAccessor
from pending_member_reminder_lib.pending_member_email_handler import PendingMemberEmailHandler

args = None


def process_input_args():
    parser = argparse.ArgumentParser(description='System to identify group leaders who need to follow up with member acceptances')

    parser.add_argument('--num_days', type=int, default=3,
                        help='Number of days before alerts should be sent')

    parser.add_argument('--send_email', '-e', action='store_true',
                        help='If present, will actual send emails to the intended recipients')

    parser.add_argument('--login_info', type=str, required=True,
                        help='Path to document on filesystem with database credentials in JSON format')

    parser.add_argument('--recipients', type=str, required=True,
                        help='Path to document on filesystem with recipients in JSON format')

    parser.add_argument('--mail_credentials', type=str, required=True,
                        help='Path to document on filesystem with information for mail connection')

    parser.add_argument('--loglevel', type=str, default='WARNING',
                        help='Logging level to use (e.g. DEBUG')

    return parser.parse_args()


def slurp_json_file_content(path_to_file):
    """
    Opens file where credentials are stored, reads file in as string, and returns it

    Does no validation on incoming data
    :param path_to_credentials: Path to file where credentials are stored
    :return: Contents of the file
    """
    file_handle = open(path_to_file)
    unvalidated_json_string = file_handle.read()
    return unvalidated_json_string


if __name__ == '__main__':
    args = process_input_args()
    logging.basicConfig(level=args.loglevel, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Pull the database login info from a secure file
    credentials_file_content = slurp_json_file_content(args.login_info)
    db_accessor = PendingMemberDbAccessor(credentials_file_content)

    # Get the list of people who need to be messaged
    # TODO:  Should this change to a wordpress datasource query, for a list of Admins on the site?
    email_recipients_json = slurp_json_file_content(args.recipients)
    email_recipients = json.loads(email_recipients_json)['send-to']
    logging.debug('Recipient list: %s' % email_recipients)

    mail_credentials_json = slurp_json_file_content(args.mail_credentials)
    mail_credentials = json.loads(mail_credentials_json)


    # Get the list of users for whom we need to be reminded
    from_dt = datetime.datetime.today() - datetime.timedelta(days=args.num_days)
    pending_users_list = db_accessor.get_list_of_users_earlier_than_datetime(from_dt=from_dt, role='pending-validation')
    if pending_users_list:
        logging.debug('First in list of pending users is %s %s %s' % (pending_users_list[0][0],
                                                                      pending_users_list[0][1],
                                                                      pending_users_list[0][2]))
    else:
        logging.info('No users in pending_users_list - everyone is allocated')
        exit(0)

    # Compose and send the email
    mailer = PendingMemberEmailHandler(recipient_list=email_recipients,
                                       pending_user_list=pending_users_list,
                                       mail_credentials=mail_credentials)
    if args.send_email:
        logging.debug('Calling send_reminders on email handler object')
        mailer.send_reminders(args.num_days)





