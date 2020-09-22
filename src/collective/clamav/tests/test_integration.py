# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from Products.validation.config import validation
from zope.component import getUtility

from collective.clamav.interfaces import IAVScanner
from collective.clamav.testing import EICAR
from collective.clamav.testing import AVMOCK_INTEGRATION_TESTING

import unittest


class TestArchetypesFunctional(unittest.TestCase):

    layer = AVMOCK_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.scanner = getUtility(IAVScanner)

    def test_validator_runs_once_per_req(self):
        # reset counter in mock scanner
        self.scanner.uses = 0
        self.assertEqual(
            'Validation failed, file is virus-infected. (Eicar-Test-Signature FOUND)',
            validation('isVirusFree', EICAR, REQUEST=self.portal.REQUEST)
        )
        self.assertEqual(1, self.scanner.uses)
        self.assertEqual(
            'Validation failed, file is virus-infected. (Eicar-Test-Signature FOUND)',
            validation('isVirusFree', EICAR, REQUEST=self.portal.REQUEST)
        )
        self.assertEqual(1, self.scanner.uses,
                         'The second scan on a request should be skipped')
