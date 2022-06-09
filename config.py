from configparser import ConfigParser

config = ConfigParser()

config.read('config.ini')

print(config.get('ResultsFolder', 'SuiviPath'))
