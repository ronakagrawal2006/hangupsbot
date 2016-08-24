import configparser
import os

config = configparser.ConfigParser()

class Properties:
  def __init__(self):
    self.environment = os.environ['ENV']
    curr_path = os.path.dirname(__file__)
    config.read(os.path.abspath(os.path.join(curr_path, 'configuration.ini')))

  def get_string(self, property_name):
    return config.get(self.environment, property_name)

  def get_boolean(self, property_name):
    return config.getboolean(self.environment, property_name)

  def get_int(self, property_name):
    return int(config.get(self.environment, property_name))