import logging

import utils



formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt = '%Y-%m-%d %H:%M:%S')


def setup_logger(name, log_file, level = logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

    
#Debugger
log_debugger = setup_logger('Debugger', '{}/debugger.log'.format(utils.path_log))

#TempoNote
log_temponote = setup_logger('TempoNote', '{}/temponote.log'.format(utils.path_log))

#TempoMonitor
log_tempomonitor = setup_logger('TempoMonitor', '{}/tempomonitor.log'.format(utils.path_log))