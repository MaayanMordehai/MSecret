#
## @package MSecret.save save informatiom moudle.
## @file save.py Implementation of @ref MSecret.save
#


## saving informatiom object
#
# object for saving informatiom from user interface objects
#
class Save(object):

    ## Constructor
    def __init__(self):
        self._password = ''
        self._recursive = False
        self._dir_name = None
        self._encryption = 'AES'
        self._should_exit = False

    ## Retrive recursive
    @property
    def recursive(self):
        return self._recursive

    ## Set recursive
    @recursive.setter
    def recursive(self, re):
        self._recursive = re

    ## Retrive password
    @property
    def password(self):
        return self._password

    ## Set password
    @password.setter
    def password(self, password):
        self._password = password

    ## Retrive dir_name
    @property
    def dir_name(self):
        return self._dir_name

    ## Retrive should_exit
    @property
    def should_exit(self):
        return self._should_exit

    ## Retrive encryption
    @property
    def encryption(self):
        return self._encryption

    ## Set dir_name
    @dir_name.setter
    def dir_name(self, name):
        self._dir_name = name

    ## Set should_exit
    @should_exit.setter
    def should_exit(self, e):
        self._should_exit = e

    ## Set encryption
    @encryption.setter
    def encryption(self, en):
        self._encryption = en
