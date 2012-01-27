// Esto es provisorio hasta que veamos una mejor implementacion

function addVideoToNITF(video){
    title = video.text();
    url = video.attr('video_url');
    if (url !== undefined ){
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
            var contenttree_window = (this).parents(".contenttreeWindow");
            var input_box = $('#'+ contenttree_window[0].id.replace(/-contenttree-window$/,"-widgets-query"));
            contenttree_window.find('.navTreeCurrentItem > a').each(function () {
                addVideoToNITF($(this));
//                 removeFromDroppable( $(this) );
            });

            $(this).contentTreeCancel();
        }
    });
    
})(jQuery);
