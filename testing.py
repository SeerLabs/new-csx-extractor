import ConfigParser
from python_wrapper import wrappers
from python_wrapper import utils

config = ConfigParser.ConfigParser()
config.read('python_wrapper/properties.config')
connectionProps = dict(config.items('ConnectionProperties'))
states = dict(config.items('States'))
wrapper = wrappers.MySQLWrapper(connectionProps, states)
wrapper.get_document_batch()
