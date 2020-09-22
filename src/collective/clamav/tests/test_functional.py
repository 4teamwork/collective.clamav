# -*- coding: utf-8 -*-
from os.path import dirname, join
from StringIO import StringIO

from collective.clamav.interfaces import IAVScannerSettings
from collective.clamav.testing import EICAR
from collective.clamav.testing import AVMOCK_AT_FUNCTIONAL_TESTING
from collective.clamav.testing import AVMOCK_DX_FUNCTIONAL_TESTING
from collective.clamav import tests

from plone.testing.z2 import Browser
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import transaction
import unittest


def getFileData(filename):
    """ return a file object from the test data folder """
    filename = join(dirname(tests.__file__), 'data', filename)
    return open(filename, 'r').read()


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        # disable auto-CSRF
        from plone.protect import auto
        auto.CSRF_DISABLED = True

        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.browser = Browser(self.layer['app'])
        self.browser.addHeader(
            'Authorization', 'Basic %s:%s' % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            )
        )

    def tearDown(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        from plone.protect import auto
        auto.CSRF_DISABLED = False


class TestArchetypesFunctional(BaseTestCase):

    layer = AVMOCK_AT_FUNCTIONAL_TESTING

    def test_atvirusfile(self):
        # Test if a virus-infected file gets caught by the validator
        self.browser.open(self.portal.absolute_url()+'/virus-folder')
        self.browser.getLink(url='createObject?type_name=File').click()
        control = self.browser.getControl(name='file_file')
        control.filename = 'virus.txt'
        control.value = StringIO(EICAR)
        self.browser.getControl('Save').click()

        self.failIf('Eicar-Test-Signature FOUND' not in self.browser.contents)

        # And let's see if a clean file passes...
        control = self.browser.getControl(name='file_file')
        control.filename = 'nonvirus.txt'
        control.value = StringIO('Not a virus')
        self.browser.getControl('Save').click()
        self.assertTrue('Changes saved' in self.browser.contents)

    def test_atvirusimage(self):
        # Test if a virus-infected image gets caught by the validator
        image_data = getFileData('image.png')
        self.browser.open(self.portal.absolute_url()+'/virus-folder')
        self.browser.getLink(url='createObject?type_name=Image').click()
        control = self.browser.getControl(name='image_file')
        control.filename = 'virus.png'
        control.value = StringIO(image_data + EICAR)
        self.browser.getControl('Save').click()

        self.assertFalse('Changes saved' in self.browser.contents)
        self.assertTrue('Eicar-Test-Signature FOUND' in self.browser.contents)

        # And let's see if a clean file passes...
        control = self.browser.getControl(name='image_file')
        control.filename = 'nonvirus.png'
        control.value = StringIO(image_data)
        self.browser.getControl('Save').click()
        self.assertTrue('Changes saved' in self.browser.contents)


class TestDexterityFunctional(BaseTestCase):

    layer = AVMOCK_DX_FUNCTIONAL_TESTING

    def test_dxvirusfile(self):
        # Test if a virus-infected file gets caught by the validator
        self.browser.open(
            self.portal.absolute_url() + '/virus-folder/++add++File')
        control = self.browser.getControl(name='form.widgets.file')
        control.filename = 'virus.txt'
        control.value = StringIO(EICAR)
        self.browser.getControl('Save').click()
        self.failIf('Eicar-Test-Signature' not in self.browser.contents)

        # And let's see if a clean file passes...
        self.browser.open(
            self.portal.absolute_url() + '/virus-folder/++add++File')
        control = self.browser.getControl(name='form.widgets.file')
        control.filename = 'nonvirus.txt'
        control.value = StringIO('Not a virus')
        self.browser.getControl('Save').click()
        self.assertTrue('Item created' in self.browser.contents)

    def test_dxvirusimage(self):
        # Test if a virus-infected image gets caught by the validator
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.browser.open(
            self.portal.absolute_url() + '/virus-folder/++add++Image')
        control = self.browser.getControl(name='form.widgets.image')
        image_data = getFileData('image.png')
        control.filename = 'virus.png'
        control.value = StringIO(image_data + EICAR)
        self.browser.getControl('Save').click()

        self.assertFalse('Changes saved' in self.browser.contents)
        self.assertTrue('Eicar-Test-Signature' in self.browser.contents)

        # And let's see if a clean file passes...
        self.browser.open(
            self.portal.absolute_url() + '/virus-folder/++add++Image')
        control = self.browser.getControl(name='form.widgets.image')
        control.filename = 'nonvirus.png'
        control.value = StringIO(image_data)
        self.browser.getControl('Save').click()
        self.assertTrue('Item created' in self.browser.contents)

    def test_disable_scanning(self):
        registry = getUtility(IRegistry)
        registry.forInterface(IAVScannerSettings).clamav_enabled = False
        transaction.commit()

        # Repeat test_atvirusimage but expect no scan
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.browser.open(
            self.portal.absolute_url() + '/virus-folder/++add++Image')
        control = self.browser.getControl(name='form.widgets.image')
        image_data = getFileData('image.png')
        control.filename = 'virus.png'
        control.value = StringIO(image_data + EICAR)
        self.browser.getControl('Save').click()

        self.assertTrue('Item created' in self.browser.contents)
        self.assertFalse('Eicar-Test-Signature' in self.browser.contents)
