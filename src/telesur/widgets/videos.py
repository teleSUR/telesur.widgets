# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer

import z3c.form.interfaces
import z3c.form.widget

from collective.formwidget.relationfield.widget \
    import ContentRelationWidget as BaseWidget

from zope.i18n import translate


class FilterVideos(BrowserView):

    def __call__(self, query=None):
        # XXX: Este import hay que tenerlo aqui dentro porque sino da un
        # loop. Lo óptimo, sería tenerlo en un archivo aparte, browser.py o
        # similar.
        from telesur.api.behavior import IAddableVideos
        field = IAddableVideos.get('relatedVideos')
        request = self.request

        widget = z3c.form.interfaces.IFieldWidget(field,
                                                  AddVideosWidget(request))
        
        result = widget.render_tree(query=query,limit=10)

        return result.strip()

class AddVideosWidget(BaseWidget):
    display_template = ViewPageTemplateFile('templates/add_videos_widget.pt')
    recurse_template = ViewPageTemplateFile('templates/recurse_videos_widget.pt')

    def render_tree(self, query=None, limit=10):
        data = []
        if query:
            url = "http://multimedia.tlsur.net/api/clip/?texto=%s&limit=%s&detalle=basico" % (query, limit)
        else:
            url = "http://multimedia.tlsur.net/api/clip/?ultimo=%s&detalle=basico" % limit

        video_api = getMultiAdapter((self.context, self.request), name="video_api")

        json = video_api.get_json(url)

        for entry in json:
            if entry['api_url']:
                # Este checkeo no debería ser necesario. Todos los videos
                # deberían tener un URL válido
                data.append(
                        {
                            'video_url': entry['api_url'],
                            'video_thumb': entry['thumbnail_mediano'],
                            'selectable': True,
                            'title': entry['titulo'],
                            'description': entry['descripcion'],
                        }
                    )

        return self.recurse_template(children=data, level=1)

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
                            firstLoad();
                        }).insertAfter($(this));
                });
                $('#%(id)s-contenttree-window').find('.contentTreeAddVideos').unbind('click').click(function () {
                    $(this).contentTreeAddVideos();
                });
                $('#%(id)s-contenttree-window').find('.contentTreeCancel').unbind('click').click(function () {
                    $(this).contentTreeCancel();
                });
                if ($('#%(id)s-widgets-query')[0] !== undefined){
                    $('#%(id)s-widgets-query').after(" ");
                }
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


    def filter_js(self):
        form_url = self.request.getURL()
        url = "%s/@@filter-related-videos" % self.context.absolute_url()

        return """\
        function filterVideos(){
        var query = document.getElementById('form-widgets-search-videos').value;
        $("ul#related-content-videos").load('%(url)s',{'query':query});
        }

        function firstLoad(){
        $("ul#related-content-videos").load('%(url)s',{});
        }
        """ % dict(url=url)


@implementer(z3c.form.interfaces.IFieldWidget)
def AddVideosFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, AddVideosWidget(request))
