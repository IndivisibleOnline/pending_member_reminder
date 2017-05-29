# pending_member_reminders

Python package that should send email reminders (etc) for members who have been waiting in the approval queues

For usage:
python pending_member_reminder.py -h

Example usage:

python pending_member_reminder.py --num_days 3 --login_info data/database_credentials.json --recipients data/pending_member_email_recipients.json  --logging_level DEBUG --mail_credentials=data/mail_handler_credentials.json --send_email

In the database, we should be able to find the list of users who haven't been approved by:

select user_id, first_name, last_name from wp_usermeta where meta_key='role' and meta_value='pending-validation'

Which you can join with wp_users:
select user_id, user_login, user_email, user_registered from wp_users where user_id=166

Not in this repository are files in the data/ directory.  All of these files should be chmod'd to only be viewable by the uid under which this app is running.
database_credentials.json:  e.g:
```
"login": "db_login_name", "password": "db_password", "dbname": "database_name"
```
mail_handler_credentials.json:
```
{
  "scopes": "https://www.googleapis.com/auth/gmail.send",
  "client_secret_file": "path_to_client_secret_json",
  "application_name": "Name of app in Gmail API",
  "sender_email": "emailof@sender.com"
}
```
pending_member_email_recipients.json:
```
{"send-to": ["recipient1@example.com", "recipient2@example.com"]}
```

pending_member_reminder_client_secret.json:  JSON file generate from Gmail API setup
