# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing import z2
from six import BytesIO
from zope.component import getGlobalSiteManager
from zope.configuration import xmlconfig
from zope.interface import implements

from collective.clamav.interfaces import IAVScanner
import collective.clamav


class CollectiveClamavLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.clamav)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.clamav:default')


COLLECTIVE_CLAMAV_FIXTURE = CollectiveClamavLayer()


COLLECTIVE_CLAMAV_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_CLAMAV_FIXTURE,),
    name='CollectiveClamavLayer:IntegrationTesting'
)


COLLECTIVE_CLAMAV_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_CLAMAV_FIXTURE,),
    name='CollectiveClamavLayer:FunctionalTesting'
)


COLLECTIVE_CLAMAV_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_CLAMAV_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveClamavLayer:AcceptanceTesting'
)

EICAR = """
    WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5E
    QVJELUFOVElWSVJVUy1URVNU\nLUZJTEUhJEgrSCo=\n""".decode('base64')


class MockAVScanner(object):
    """Mock objects to run tests withoud clamav present.
    """

    implements(IAVScanner)

    uses = 0

    def ping(self, type, **kwargs):
        """
        """
        return True

    def scanStream(self, stream, type, **kwargs):
        """
        """
        self.uses += 1
        if EICAR in stream.read():
            return 'Eicar-Test-Signature FOUND'
        return None

    def scanBuffer(self, buffer, type, **kwargs):
        """
        """
        return self.scanStream(BytesIO(buffer), type, **kwargs)


class AVFixture(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import collective.clamav
        xmlconfig.file('configure.zcml', collective.clamav,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.clamav:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'virus-folder')
        setRoles(portal, TEST_USER_ID, ['Member'])



AV_DX_FIXTURE = AVFixture(name="AV_DX_Fixture")
AV_AT_FIXTURE = AVFixture(bases=(PLONE_FIXTURE, ), name="AV_AT_Fixture")


class AVMockFixture(PloneSandboxLayer):

    defaultBases = (AV_DX_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        gsm = getGlobalSiteManager()
        gsm.registerUtility(MockAVScanner())


AVMOCK_DX_FIXTURE = AVMockFixture(name="AVMOCK_DX_Fixture")
AVMOCK_AT_FIXTURE = AVMockFixture(bases=(AV_AT_FIXTURE, ), name="AVMOCK_AT_Fixture")

AV_INTEGRATION_TESTING = IntegrationTesting(
    bases=(AV_DX_FIXTURE, ), name="AVFixture:Integration")
AV_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(AV_DX_FIXTURE, ), name="AVFixture:Functional")
AVMOCK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(AVMOCK_DX_FIXTURE, ), name="AVMockFixture:Integration")
AVMOCK_AT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(AVMOCK_AT_FIXTURE, ), name="AVMockATFixture:Functional")
AVMOCK_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(AVMOCK_DX_FIXTURE, ), name="AVMockDXFixture:Functional")
