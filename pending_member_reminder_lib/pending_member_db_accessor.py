import json
import MySQLdb
import logging

class PendingMemberDbAccessor():

    def __init__(self, db_credentials):
        """
        Constructor for database accessor object

        Potentially throws ValueError if db_credentials is an invalid JSON string
        :param db_credentials: JSON string containing db credentials
        :return: None
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # Verify that we have a valid JSON document passed as db credentials
        self.db_credentials_dict = json.loads(db_credentials)

        # Verify content (do we have all the fields we expect
        if not self.db_credentials_dict.has_key('dbname') or \
           not self.db_credentials_dict.has_key('login') or \
           not self.db_credentials_dict.has_key('password'):
            raise ValueError('Invalid credential set passed in')

        self.database = self.db_credentials_dict['dbname']
        self.login = self.db_credentials_dict['login']
        self.passwd = self.db_credentials_dict['password']

        try:
            self.db_connection = MySQLdb.connect(user=self.login, passwd=self.passwd, db=self.database)
        except MySQLdb.OperationalError as e:
            logging.error('Could not connect to db: %s' % e.message)

        if not self._verify_wordpress_db_structure():
            logging.error('Unable to validate database structure.  Aborting')
        return



    def _verify_wordpress_db_structure(self):
        """
        This function checks that the structure of the wordpress installation is as expected
        (Do the tables it relies on exist?  Does a test query run properly?)

        :return:  True if the self-testing works, False if there was some problem
        """

        # First check that the tables are extant
        table_query = 'SELECT table_name FROM information_schema.tables '\
                      'where table_name in ("wp_users", "wp_usermeta", "wp_term_taxonomy", "wp_terms")'
        c = self.db_connection.cursor()
        c.execute(table_query)
        if c.rowcount != 4:
            logging.error('Expected table set not found in %s' % self.database)
            return False

        self.logger.debug('Wordpress database structure verified')
        return True

    def _get_list_of_local_groups(self):
        """
        Hit the db for a complete list of the local groups
        TODO: I think this might end up being unused....

        :return: A list of tuples, first element of which is the term_id and the second is the name of the group
        """
        local_group_query = 'select wp_term_taxonomy.term_id, wp_terms.name '\
                            'from wp_term_taxonomy, wp_terms ' \
                            'where wp_terms.term_id = wp_term_taxonomy.term_id ' \
                            'AND wp_term_taxonomy.taxonomy="local_groups" ' \
                            'order by name ASC'

        c = self.db_connection.cursor()
        c.execute(local_group_query)

        # Am comfortable doing this bc the number of records in the db should always be relatively low
        response = c.fetchall()

        self.logger.info('%d local groups found' % len(response))
        return response

    def _get_list_of_users_earlier_than_datetime(self, from_dt, role='pending-validation'):
        """
        Returns a list of users of a given role in the database whos accounts were created before a given datetime

        Default status is 'pending-validation'
        To see complete list of available roles:  select distinct(meta_value) from wp_usermeta where meta_key='role';

        :param from_dt: Datetime object - any user of the given status from before this date time should be returned
        :param role: String defining user role (storage format in database
        :return: A list of user tuples (id, name, email) (or None if there were no users found meeting criteria)
        """
        user_query = 'select id, user_nicename, user_email from wp_users '\
                     'where id in '\
                     '(select user_id from wp_usermeta where meta_key="role" and meta_value="%s")' \
                     'and user_registered<"%s"' % (role, from_dt)

        self.logger.debug('User list query: %s' % user_query)
        c = self.db_connection.cursor()
        rowcount = c.execute(user_query)

        if not rowcount:
            self.logger.info('No users found meeting criteria: role=%s, from_dt=%s' % (role, from_dt))
            return None

        return c.fetchall()








