import logging
from flask import current_app

# logging.basicConfig(filename="std.log", format='%(asctime)s %(message)s', filemode='w') 
logger = logging.getLogger(__name__)

def logFun(message):
    current_app.logger.info(message)