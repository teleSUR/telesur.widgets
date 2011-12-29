from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class TelesurWidgets(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import telesur.widgets
        xmlconfig.file('configure.zcml',
                       telesur.widgets,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'telesur.widgets:default')

TELESUR_WIDGETS_FIXTURE = TelesurWidgets()
TELESUR_WIDGETS_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(TELESUR_WIDGETS_FIXTURE, ),
                       name="TelesurWidgets:Integration")