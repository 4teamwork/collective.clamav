# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from collective.clamav import _
from collective.clamav.interfaces import IAVScannerSettings


class ClamavControlPanelForm(controlpanel.RegistryEditForm):
    schema = IAVScannerSettings
    label = _(u'Clamav Plone Settings')
    description = _(u"""""")

    def updateFields(self):
            super(ClamavControlPanelForm, self).updateFields()

    def updateWidgets(self):
            super(ClamavControlPanelForm, self).updateWidgets()


class ClamavControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ClamavControlPanelForm
