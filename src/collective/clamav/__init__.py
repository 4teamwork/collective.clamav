# -*- coding: utf-8 -*-
"""Init and utils."""
from Products.validation import validation
from zope.i18nmessageid import MessageFactory

import logging

_ = MessageFactory('collective.clamav')


# This import causes problems importing `_` if it comes before the line above
from collective.clamav.validator import ClamavValidator  # noqa
validation.register(ClamavValidator('isVirusFree'))

logger = logging.getLogger('collective.clamav')
logger.setLevel(logging.INFO)
fh = logging.handlers.TimedRotatingFileHandler('collective.clamav.log', when='d', backupCount=7)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
