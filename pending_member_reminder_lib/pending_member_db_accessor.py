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

        return True

    def _get_list_of_local_groups(self):
        """
        Hit the db for a complete list of the local groups
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

        return response




