// Esto es provisorio hasta que veamos una mejor implementacion
function addVideoToNITF(video){
    title = video.text();
    url = video.attr('href');
    if ( title != "" && url !== undefined ){
        jQuery.ajax({type: 'POST',
                        url: '@@add-video-to-context',
                        async : false,
                        data: {'title':title,
                               'url':url},
                        success: function(results){
                            // Necesitamos hacer algo con el resultado ?
                                }
                    });
    }
}

if(jQuery) (function($){
    
    $.extend($.fn, {
        contentTreeAddVideos: function() {
            $("#content-droppable > li > a.ui-widget-content").each(function () {
                addVideoToNITF($(this));
                removeVideoFromDroppable($(this));
            });

            $(this).contentTreeCancel();
            window.location.reload();
        }
    });
    
})(jQuery);
