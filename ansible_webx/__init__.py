import configparser
from os import path

config = configparser.ConfigParser()
config_path = path.dirname(path.realpath(__file__))
config.read(f'{config_path}/config.ini')
