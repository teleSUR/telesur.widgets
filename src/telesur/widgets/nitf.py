# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer

import z3c.form.interfaces
import z3c.form.widget
from z3c.form import field

from collective.formwidget.relationfield.widget \
                                 import ContentRelationWidget as BaseWidget


class ContentRelationWidget(BaseWidget):
    input_template = ViewPageTemplateFile('templates/nitf_related_input.pt')


@implementer(z3c.form.interfaces.IFieldWidget)
def ContentRelationFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, ContentRelationWidget(request))
