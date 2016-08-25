
import logging
import graypy

from config import FILE_LOGGING, GRAY_LOGGING

def setup_logging(configs, process_name="default_process"):
    if configs['log']['logtype'] == FILE_LOGGING:
       log_name = "%s_%s.log" % (configs['redis']['builder'],configs['log']['fileName'])
       logging.basicConfig(filename = log_name, level=logging.DEBUG)
       logging.basicConfig(level=logging.DEBUG)
    elif configs['log']['logtype'] == GRAY_LOGGING:
       # print "I choose Graylog!"
       main_logger = logging.getLogger()
       main_logger.setLevel(logging.DEBUG)
       handler = graypy.GELFHandler(configs['log']['host'], int(configs['log']['port']), localname=process_name)
       main_logger.addHandler( handler )
       main_logger.addHandler( logging.StreamHandler() )
