# -*- coding: utf-8 -*-
__author__ = 'Vitalii Turovets'

import optparse
from optparse import OptionParser
import ConfigParser
import MySQLdb
import getpass
import os


class ConfigError(Exception):
    def __init__(self, message):
        self.message = message


class UserError(Exception):
    def __init__(self, message):
        self.message = message

class Config():
    def __init__(self):
            filename = "server.conf"
            self.possible_actions = ['add', 'modify', 'delete']
            self.required_action = None
            self.parser = OptionParser()
            self.parser.set_usage("""Usage: python manage-users.py [OPTIONS] [ACTION] [username]

Options:
  -h, --help   show this help message and exit
  -f FILENAME  proxy server configuration file (default: server.conf)

Actions:
  add			: add user
  modify		: change user password
  delete		: delete user""")
            self.parser.add_option("-f", dest="filename", help="proxy server configuration file (default: server.conf)")

            self.help_message = self.parser.format_help()
            try:
                options, args = self.parser.parse_args()
                options = options.__dict__
                if options['filename'] is not None:
                    filename = options['filename']
            except ValueError:
                raise ConfigError("Not sure what to do, options incorrect.")
            if len(args) < 2:
                raise ConfigError("Not enough parameters, use -h flag for help.")
            if args[0] not in self.possible_actions:
                raise ConfigError("Could not understand '%s' action, use -h flag for help." % args[0])

            self.action = args[0]
            self.username = args[1]
            MySQLdb.escape_string(self.username)

            path = os.path.realpath(os.path.curdir)
            path = os.path.join(path, filename)
            if not os.path.isfile(path):
                raise ConfigError("Configfile %s not found!" % path)

            self.db_config = dict()
            parser_instance = ConfigParser.ConfigParser()
            parser_instance.read(filename)
            self.db_config = {
                'host': parser_instance.get('database', 'host'),
                'database': parser_instance.get('database', 'database'),
                'username': parser_instance.get('database', 'username'),
                'password': parser_instance.get('database', 'password')
            }

    def __call__(self):
        return self.db_config

    def __getitem__(self, item):
        return self.db_config[item]


class UserManager():
    def __init__(self, db_config):
        self.db_config = db_config
        self.db = MySQLdb.connect(
            host=db_config['host'],
            user=db_config['username'],
            passwd=db_config['password'],
            db=db_config['database'],
            charset='utf8')
        self.cursor = self.db.cursor()

    def user_exists(self, user):
        query = "SELECT User FROM users WHERE User='%s'" % user
        self.cursor.execute(query)
        if user in str(self.cursor.fetchone()):
            return True
        else:
            return False

    def modify(self, user):
        if not self.user_exists(user):
            raise UserError("user '%s' does not exist." % user)
        password = UserManager.ask_pass()
        query = "UPDATE users SET Password=PASSWORD('%s') WHERE User='%s'" % (password, user)
        self.cursor.execute(query)
        self.db.commit()
        return "User '%s' modified" % user

    def add(self, user):
        if self.user_exists(user):
            raise UserError("User '%s' exists." % user)
        password = UserManager.ask_pass()
        query = "INSERT INTO users (User,Password) VALUES ('%s',PASSWORD('%s'))" % (user, password)

        self.cursor.execute(query)
        self.db.commit()
        return "User '%s' created." % user

    def delete(self, user):
        if not self.user_exists(user):
            raise UserError("user '%s' does not exist." % user)
        query = "DELETE FROM users WHERE User='%s'" % user
        self.cursor.execute(query)
        self.db.commit()
        return "User '%s' deleted." % user

    @staticmethod
    def ask_pass():
        password1 = getpass.getpass("Please input user password: ")
        password2 = getpass.getpass("Please input password again: ")
        if password1 == password2:
            MySQLdb.escape_string(password1)
            return password1
        else:
            raise UserError("Passwords mismatch!")

if __name__ == '__main__':
    try:
        config = Config()
        mgr = UserManager(config())
        ActionToCall = getattr(mgr, config.action)
        print ActionToCall(config.username)

    except ConfigParser.NoSectionError, e:
        print "Database config section not found!"

    except ConfigParser.NoOptionError, e:
        print "Option %s in %s section not found." % e.option, e.section

    except IOError, e:
        print "IO Error: %s" % e.message

    except OSError, e:
        print "OS Error %d: %s" % e.errno, e.message

    except ConfigError, e:
        print "Configuration error: %s" % e.message

    except optparse.OptionError, e:
        print "CLI Optiohs error %s" % e.message

    except UserError, e:
        print "User error: %s" % e.message

    except MySQLdb.MySQLError, e:
        print "MySQL Error: %s" % str(e.args)

    except MySQLdb.Error, e:
        print "DB Error %s" % str(e.args)
