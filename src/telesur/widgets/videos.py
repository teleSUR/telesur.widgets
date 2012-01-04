# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer

import z3c.form.interfaces
import z3c.form.widget
from z3c.form import field

from collective.formwidget.relationfield.widget \
                                 import ContentRelationWidget as BaseWidget


from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree


class AddVideosWidget(BaseWidget):
    display_template = ViewPageTemplateFile('templates/add_videos_widget.pt')

    def render_tree(self, relPath=None, query=None, limit=10):
        # Todo lo de aqui abajo tiene que ser reemplazado por una query
        # que traiga el listado de videos.
        content = self.context
        portal_state = getMultiAdapter((self.context, self.request),
                                          name=u'plone_portal_state')
        portal = portal_state.portal()
        source = self.bound_source
        if query is not None:
            source.navigation_tree_query = query
        strategy = getMultiAdapter((portal, self), INavtreeStrategy)
        if relPath is not None:
            root_path = portal_state.navigation_root_path()
            rel_path = root_path + '/' + relPath
            strategy.rootPath = rel_path
        data = buildFolderTree(portal,
                               obj=portal,
                               query=source.navigation_tree_query,
                               strategy=strategy)

        return self.recurse_template(
                                    children=data.get('children', [])[:limit],
                                    level=1)
                                    
@implementer(z3c.form.interfaces.IFieldWidget)
def AddVideosFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, AddVideosWidget(request))
