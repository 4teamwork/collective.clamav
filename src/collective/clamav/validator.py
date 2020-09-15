# -*- coding: utf-8 -*-
import logging

import Globals
from Products.validation.interfaces.IValidator import IValidator
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implements, Invalid
from collective.clamav.interfaces import IAVScanner
from collective.clamav.scanner import ScanError
from collective.clamav.interfaces import IAVScannerSettings

logger = logging.getLogger('collective.clamav')


def _scanBuffer(buffer):

    registry = getUtility(IRegistry)
    settings = registry.forInterface(IAVScannerSettings, check=False)
    if settings is None or not settings.clamav_enabled:
        return ''
    scanner = getUtility(IAVScanner)

    if settings.clamav_connection == 'net':
        result = scanner.scanBuffer(
            buffer, 'net',
            host=settings.clamav_host,
            port=int(settings.clamav_port),
            timeout=float(settings.clamav_timeout))
    else:
        result = scanner.scanBuffer(buffer, 'socket',
                                    socketpath=settings.clamav_socket,
                                    timeout=float(settings.clamav_timeout))

    return result


class ClamavValidator:
    """Archetypes validator to confirm a file upload is virus-free."""

    implements(IValidator)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        if hasattr(value, 'getBlob'):
            # the value can be a plone.app.blob.field.BlobWrapper
            # in which case we open the blob file to provide a file interface
            # as used for FileUpload
            file_value = value.getBlob().open()
        else:
            file_value = value

        if hasattr(file_value, 'seek'):
            # when submitted a new 'file_value' is a
            # 'ZPublisher.HTTPRequest.FileUpload'

            prev_scan_result = getattr(value, '_validate_isVirusFree', None)
            if prev_scan_result is not None:
                # validation is called in mutator (setFile()) to *ensure*
                # we never miss it, but the results are more user friendly if
                # they are returned from validation code
                return prev_scan_result

            file_value.seek(0)
            # TODO this reads the entire file into memory, there should be
            # a smarter way to do this
            content = file_value.read()
            result = ''
            try:
                result = _scanBuffer(content)
            except ScanError as e:
                logger.error('ScanError %s on %s.' % (e, file_value.filename))
                return "There was an error while checking the file for " \
                       "viruses: Please contact your system administrator."

            if result:
                value._validate_isVirusFree = False
                return "Validation failed, file is virus-infected. (%s)" % \
                       (result)
            else:
                # mark the file upload instance as already checked
                value._validate_isVirusFree = True
                return True
        else:
            # if we kept existing file
            return True


try:
    from z3c.form import validator
    from plone.namedfile.interfaces import INamedField
    from plone.formwidget.namedfile.interfaces import INamedFileWidget
    from plone.formwidget.namedfile.validator import NamedFileWidgetValidator
except ImportError:
    pass
else:

    class Z3CFormclamavValidator(NamedFileWidgetValidator):
        """z3c.form validator to confirm a file upload is virus-free."""

        def validate(self, value):
            super(Z3CFormclamavValidator, self).validate(value)

            if getattr(value, '_validate_isVirusFree', False) or value is None:
                # validation is called multiple times for the same file upload
                return

            # TODO this reads the entire file into memory, there should be
            # a smarter way to do this
            result = ''
            try:
                result = _scanBuffer(value.data)
            except ScanError as e:
                logger.error('ScanError %s on %s.' % (e, value.filename))
                raise Invalid("There was an error while checking "
                              "the file for viruses: Please "
                              "contact your system administrator.")

            if result:
                raise Invalid("Validation failed, file "
                              "is virus-infected. (%s)" %
                              (result))
            else:
                # mark the file instance as already checked
                value._validate_isVirusFree = True

    validator.WidgetValidatorDiscriminators(Z3CFormclamavValidator,
                                            field=INamedField,
                                            widget=INamedFileWidget)
