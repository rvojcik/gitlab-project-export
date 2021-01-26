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
        self.config_process()
        self.config_close()

    def config_open(self):
        try:
            self.conf_fh = open(self.config_file, 'r')
        except IOError as e:
            print("({})".format(e))
            sys.exit(1)

    def config_close(self):
        self.conf_fh.close()

    def config_process(self):
        """ Process configuration file, mainly to maintain backwards compatibility of new features """
        ssl_verify_default = True
        # Set default if not exist
        if not self.config['gitlab']['access'].__contains__('ssl_verify'):
            self.config['gitlab']['access']['ssl_verify'] = ssl_verify_default
        
        # Better safe then sorry. If file or directory not exist set default
        if isinstance(self.config['gitlab']['access']['ssl_verify'], str):
            if not os.path.exists(self.config['gitlab']['access']['ssl_verify']):
                print("WARNING: provided path to ssl bundle not exist, setting to %s" % (str(ssl_verify_default)), file=sys.stderr)
                self.config['gitlab']['access']['ssl_verify'] = ssl_verify_default

    def config_load(self):
        self.config = yaml.load(self.conf_fh.read(), Loader=yaml.FullLoader)

