# -*- coding: utf-8 -*-
"""Init and utils."""
from App.config import getConfiguration
from Products.validation import validation
from zope.i18nmessageid import MessageFactory
# This TimedRotatingFileHandler "supports reopening of logs.”
from ZConfig.components.logger.loghandler import TimedRotatingFileHandler

import logging
import os.path

root_logger = logging.root
_ = MessageFactory('collective.clamav')


# This import causes problems importing `_` if it comes before the line above
from collective.clamav.validator import ClamavValidator  # noqa
validation.register(ClamavValidator('isVirusFree'))

def get_log_dir_path():
    """Determine the path of the deployment's var/log/ directory.
    This will be derived from Zope2's EventLog location, in order to not
    have to figure out the path to var/log/ ourselves from buildout.
    """
    zconf = getConfiguration()
    eventlog = getattr(zconf, 'eventlog', None)
    if eventlog is None:
        return None

    handler_factories = eventlog.handler_factories
    eventlog_path = handler_factories[0].section.path
    log_dir = os.path.dirname(eventlog_path)
    return log_dir

logger = logging.getLogger('collective.clamav')
logger.setLevel(logging.INFO)

log_path = get_log_dir_path()
if log_path:
    fh = TimedRotatingFileHandler(
        os.path.join(log_path, 'collective.clamav.log'), when='d', backupCount=7
    )
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
else:
    root_logger.error('')
    root_logger.error(
        "collective.clamav: Couldn't find eventlog configuration in order "
        "to determine logfile location!")
    root_logger.error(
        "collective.clamav: No clamav logfile will be written!")
    root_logger.error('')
