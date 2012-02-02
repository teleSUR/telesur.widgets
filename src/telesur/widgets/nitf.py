# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer

import z3c.form.interfaces
import z3c.form.widget

from collective.formwidget.relationfield.widget \
    import ContentRelationWidget as BaseWidget

from Products.CMFCore.utils import getToolByName
    
from plone.formwidget.autocomplete.widget import AutocompleteSearch
from plone.app.vocabularies.catalog import parse_query

from plone.app.layout.navigation.navtree import buildFolderTree

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.formwidget.contenttree.navtree import NavtreeStrategy

from DateTime import DateTime

class NITFTreeStrategy(NavtreeStrategy):
    
    def decoratorFactory(self, node):
        new_node = super(NITFTreeStrategy, self).decoratorFactory(node)
        # Pongamos la fecha en un objeto "usable"
        new_node['creation_date'] = DateTime(new_node['creation_date'])
        # Y agregamos la sección del NITF
        new_node['section'] = getattr(node['item'], 'section', "")

        return new_node
        

class FilterRelatedNitf(BrowserView):

    def __call__(self, query=None, offset=0):
        base_query = {'portal_type': 'collective.nitf.content',
                      'sort_on': 'modified',
                      'sort_order': 'reverse',
                      'review_state': 'published'}

        if query:
            base_query.update(parse_query(query))

        result = self.context.render_tree(relPath='articulos',
                                          query=base_query,
                                          limit=10,
                                          offset=int(offset))

        return result.strip()


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
    recurse_template = ViewPageTemplateFile('templates/nitf_related_recurse.pt')

    def render_tree(self, relPath=None, query=None, limit=10, offset=0):
        content = self.context
        portal_state = getMultiAdapter((self.context, self.request),
                                          name=u'plone_portal_state')
        portal = portal_state.portal()
        source = self.bound_source
        if query is not None:
            source.navigation_tree_query = query

        strategy = getMultiAdapter((portal, self),
                                   INavtreeStrategy,
                                   name="nitf-tree-strategy")

        if relPath is not None:
            root_path = portal_state.navigation_root_path()
            rel_path = root_path + '/' + relPath
            strategy.rootPath = rel_path
        
        data = buildFolderTree(portal,
                               obj=portal,
                               query=source.navigation_tree_query,
                               strategy=strategy)

        return self.recurse_template(
                        children=data.get('children', [])[offset:offset+limit],
                        level=1,
                        offset=offset+limit)

    def autocomplete_url(self):
        """
        Vamos a generar nuestra propia busqueda para el autocomplete
        """
        form_url = self.request.getURL()

        return "%s/++widget++%s/@@nitf-autocomplete-search" % (
            form_url, self.name )

    def filter_js(self):
        form_url = self.request.getURL()
        url = "%s/++widget++%s/@@filter-related-nitf" % (form_url, self.name)

        return """\
        function filterNITF(){
        var query = document.getElementById('form-widgets-search-nitf-related').value;
        $("ul#related-content-nitf").load('%(url)s',{'query':query});
        }
        
        function removeNITFFromDroppable( $item ) {
            var $dropping = jq('#content-droppable');
            var $listing = jq('.contenttreeWidget .navTree');
            var $item_href = $item.find('a.ui-widget-content').attr('href');
            var $listing_item = $('.contenttreeWidget a@[href='+$item_href+']').parent();
            $listing_item.removeClass('navTreeCurrentItem');
            $listing_item.addClass("draggable");
            $item.remove();
        }

        function unbindClickEvent() {

            $('ul#content-droppable').unbind('click').click(function(event) {
                var $item = $(this);
                var $target = $(event.target);
                var $parent = $($target).parent();

                if ( $target.is("a.ui-icon-trash") ) {
                    removeNITFFromDroppable($parent);
                    return false
                    }
                if ( $target.is("a.ui-widget-content") ) {
                    return false
                    }
            });

            $('ul#related-content-nitf > li > a').unbind('click').click(function(event) {
                return false

            });

        }
        
        function appendMoreNitf(offset) {
            $("#show-more-results").remove();
            var query = document.getElementById('form-widgets-search-nitf-related').value;

            jQuery.ajax({type: 'POST',
                        url: '%(url)s',
                        async : true,
                        data: {'query':query,
                                'offset':offset},
                        success: function(results){
                                $("ul#related-content-nitf").append(results);
                                unbindClickEvent();
                                }
                            });
        }
        """ % dict(url=url)

            
@implementer(z3c.form.interfaces.IFieldWidget)
def ContentRelationFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, ContentRelationWidget(request))
