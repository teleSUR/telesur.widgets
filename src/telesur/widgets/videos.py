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

from telesur.api.interfaces import IPortalAPI
from zope.component import queryUtility
from zope.i18n import translate

class AddVideosWidget(BaseWidget):
    display_template = ViewPageTemplateFile('templates/add_videos_widget.pt')
    recurse_template = ViewPageTemplateFile('templates/recurse_videos_widget.pt')

    def render_tree(self, limit=10):
        data = []
        url = "http://multimedia.tlsur.net/api/clip/?ultimo=%s"%limit

        video_api = getMultiAdapter((self.context, self.request), name="video_api")

        json = video_api.get_json(url)

        for entry in json:
            if entry['archivo_url']:
                # Este checkeo no debería ser necesario. Todos los videos
                # deberían tener un URL válido
                data.append(
                        {
                            'video_url' : entry['archivo_url'],
                            'video_thumb' : entry['thumbnail_mediano'],
                            'selectable' : True,
                            'description' : entry['descripcion'],
                        }
                    )
                    
        return self.recurse_template(children=data,level=1)


    def js_extra(self):
        form_url = self.request.getURL()
        url = "%s/++widget++%s/@@contenttree-fetch" % (form_url, self.name)

        return """\

                $('#%(id)s-widgets-query').each(function() {
                    if($(this).siblings('input.searchButton').length > 0) { return; }
                    $(document.createElement('input'))
                        .attr({
                            'type': 'button',
                            'value': '%(button_val)s'
                        })
                        .addClass('searchButton')
                        .click( function () {
                            var parent = $(this).parents("*[id$='-autocomplete']")
                            var window = parent.siblings("*[id$='-contenttree-window']")
                            window.showDialog();
                        }).insertAfter($(this));
                });
                $('#%(id)s-contenttree-window').find('.contentTreeAddVideos').unbind('click').click(function () {
                    $(this).contentTreeAddVideos();
                });
                $('#%(id)s-contenttree-window').find('.contentTreeCancel').unbind('click').click(function () {
                    $(this).contentTreeCancel();
                });
                $('#%(id)s-widgets-query').after(" ");
                $('#%(id)s-contenttree').contentTree(
                    {
                        script: '%(url)s',
                        folderEvent: '%(folderEvent)s',
                        selectEvent: '%(selectEvent)s',
                        expandSpeed: %(expandSpeed)d,
                        collapseSpeed: %(collapseSpeed)s,
                        multiFolder: %(multiFolder)s,
                        multiSelect: %(multiSelect)s,
                    },
                    function(event, selected, data, title) {
                        // alert(event + ', ' + selected + ', ' + data + ', ' + title);
                    }
                );
        """ % dict(url=url,
                   id=self.name.replace('.', '-'),
                   folderEvent=self.folderEvent,
                   selectEvent=self.selectEvent,
                   expandSpeed=self.expandSpeed,
                   collapseSpeed=self.collapseSpeed,
                   multiFolder=str(self.multiFolder).lower(),
                   multiSelect=str(self.multi_select).lower(),
                   name=self.name,
                   klass=self.klass,
                   title=self.title,
                   button_val=translate(
                       u'heading_contenttree_browse',
                       default=u'Browse for items',
                       domain='collective.formwidget.relationfield',
                       context=self.request))
    

@implementer(z3c.form.interfaces.IFieldWidget)
def AddVideosFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, AddVideosWidget(request))
