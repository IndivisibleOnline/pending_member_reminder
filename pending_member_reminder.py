import argparse
import logging

from pending_member_reminder_lib.pending_member_db_accessor import PendingMemberDbAccessor

args = None


def process_input_args():
    parser = argparse.ArgumentParser(description='System to identify group leaders who need to follow up with member acceptances')

    parser.add_argument('--num_days', type=int, default=3,
                        help='Number of week days before alerts should be sent')
    parser.add_argument('--send_email', '-e', action='store_true',
                        help='If present, will actual send emails to the intended recipients')
    parser.add_argument('--login_info', type=str, required=True,
                        help='Path to document on filesystem with database credentials in JSON format')

    return parser.parse_args()


def slurp_db_credentials(path_to_credentials):
    """
    Opens file where credentials are stored, reads file in as string, and returns it

    Does no validation on incoming data
    :param path_to_credentials: Path to file where credentials are stored
    :return: Contents of the file
    """
    credentials_file = open(path_to_credentials)
    unvalidated_json_string = credentials_file.read()
    return unvalidated_json_string


if __name__ == '__main__':
    args = process_input_args()

    # Pull the database login info from a secure file
    credentials_file_content = slurp_db_credentials(args.login_info)
    db_accessor = PendingMemberDbAccessor(credentials_file_content)

    # Get the list of groups

    # Get the list of team leaders who
