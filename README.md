# pending_member_reminders

Python package that should send email reminders (etc) for members who have been waiting in the approval queues

For usage:
python pending_member_reminder.py -h



In the database, we should be able to find the list of users who haven't been approved by:

select user_id, first_name, last_name from wp_usermeta where meta_key='role' and meta_value='pending-validation'

Which you can join with wp_users:
select user_id, user_login, user_email, user_registered from wp_users where user_id=166