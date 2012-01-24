# -*- coding: utf-8 -*-

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer

import z3c.form.interfaces
import z3c.form.widget

from collective.formwidget.relationfield.widget \
    import ContentRelationWidget as BaseWidget

from Products.CMFCore.utils import getToolByName
    
from plone.formwidget.autocomplete.widget import AutocompleteSearch
from plone.app.vocabularies.catalog import parse_query

class ContentRelationAutocomplete(AutocompleteSearch):

    def __call__(self):
        query = self.request.get('q', None)

        # Vamos a crear nuestro propio filtro y a ignorar el funcionamiento
        # de AutocompleteSearch
        if query:
            # Si hay una query, actualizamos el valor para filtrar solo
            # en la carpeta 'articulos'
            query += ' path:/articulos'
        else:
            return ''

        portal_tool = getToolByName(self.context.form.context, "portal_url")
        portal_path = portal_tool.getPortalPath()
        
        custom_query = parse_query(query, portal_path)
        custom_query.update({'portal_type':['collective.nitf.content'],
                             'sort_on':'modified',
                             'sort_order':'reverse',
                             'review_state':'published'})

        portal_catalog = getToolByName(self.context.form.context,
                                       "portal_catalog")

        brains = portal_catalog(**custom_query)
        
        source = self.context.bound_source
        results = (source.getTermByBrain(brain, real_value=False)
                   for brain in brains)

        return '\n'.join(["%s|%s" % (t.token, t.title or t.token)
                            for t in results])

class ContentRelationWidget(BaseWidget):
    """
    """
    input_template = ViewPageTemplateFile('templates/nitf_related_input.pt')

    def autocomplete_url(self):
        """
        Vamos a generar nuestra propia busqueda para el autocomplete
        """
        form_url = self.request.getURL()

        return "%s/++widget++%s/@@nitf-autocomplete-search" % (
            form_url, self.name )

@implementer(z3c.form.interfaces.IFieldWidget)
def ContentRelationFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, ContentRelationWidget(request))
