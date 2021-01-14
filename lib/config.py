from __future__ import print_function
import yaml
import os
import sys


class Config:
    '''Load configuration from yaml file'''

    def __init__(self, config_file):
        '''Init config object'''

        self.config_file = config_file
        self.config_open()
        self.config_load()
        self.config_close()

    def config_open(self):
        try:
            self.conf_fh = open(self.config_file, 'r')
        except IOError as e:
            print("({})".format(e))
            sys.exit(1)

    def config_close(self):
        self.conf_fh.close()

    def config_load(self):
        self.config = yaml.load(self.conf_fh.read(), Loader=yaml.FullLoader)
