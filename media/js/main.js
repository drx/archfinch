(function($) {
  $.fn.disableTextSelect = function() {
      return this.each(function(){
        if($.browser.mozilla){//Firefox
          $(this).css("MozUserSelect","none");
        }else if($.browser.msie){//IE
          $(this).bind("selectstart",function(){return false;});
        }else{//Opera, etc.
          $(this).mousedown(function(){return false;});
        }
      });
  }
  $(function($){
      $(".rating,.rating_small").disableTextSelect();
  });
  $.fn.getText = function() {
    return $(this).contents().map(function(){if (this.nodeType == 3) return this.nodeValue;}).get().join('')
  }
})(jQuery); 

editlink = "<a href='' class='edit'>edit</a>";
textarealink = "<a href='' class='edit' editable='textarea'>edit</a>";
removelink = "<a href='' class='remove'>remove</a>";
textareaajax = "<img src='/media/images/ajax-loader.gif' class='nodisplay loading'><div class='error'></div>";

function additem(id, name, url, annotation, annotation_processed)
{
    if (annotation)
    {
        p = "<div class='annotation editable textarea'><div markdown='"+annotation.replace(/'/g, "&apos;")+"'>"+annotation_processed+"</div>"+textareaajax+"</div>";
    }
    else
    {
        p = "<div class='annotation editable noedit noremove'><div markdown=''></div><a href='' class='edit' editable='textarea'>Add annotation</a>"+textareaajax+"</div>";
    }
    $("#list").append("<div class='box opinion widebox editable noedit noremove' id='item_"+id+"'><div class='title'><a class='title' href='"+url+"'>"+name+"</a></div><a href='' class='remove'>remove</a>"+p+"</div>");
}

function addheading(text, addlinks)
{
    $("#list").append("<h2 class='editable'>"+text+(addlinks?editlink+removelink:'')+"</h2>");
    $("#add_text").val("");
}
function addtext(markdown, processed, addlinks)
{
    $("#list").append("<div class='editable textarea'><div markdown='"+markdown.replace(/'/g, "&apos;")+"'>"+processed+"</div>"+(addlinks?textarealink+removelink+textareaajax:'')+"</div>");
}

/* serialize a sorted list */
function list_serialize()
{
    var a = "";
    a += "title="+encodeURIComponent($("#list_title").getText());
    a += "&list_id="+$("#list").attr("list_id");
    $("#list").children().each(function(i)
    {
        a += "&a=";
        if ($(this).is('h2'))
        {
            a += "heading_"+encodeURIComponent($(this).getText());
        }
        else if ($(this).is('.textarea'))
        {
            a += "text_"+encodeURIComponent($(this).children('div').attr('markdown'));
        }
        else
        {
            a += $(this).attr("id");
            $(this).children(".annotation").each(function(i)
            {
                if ($(this).children('div').length)
                {
                    v = encodeURIComponent($(this).children('div').attr('markdown'));
                    if (v.length)
                        a += "_"+v;
                }
            });
        }
    });
    return a;
}

function get_item_id(self)
{
    return $(self).parents(".opinion").attr("item")
}

function get_seq_term(self)
{
    return $(self).parents(".opinion").attr("seq_term")
}

function rating_to_hint(obj)
{
    if (obj.is('img'))
    {
        r = 'list';
    }
    else
    {   
        r = obj.html();
    }
    switch (r)
    {
        case '1': return 'Hate it'
        case '2': return 'Dislike it'
        case '3': return 'Neutral to it'
        case '4': return 'Like it'
        case '5': return 'Love it'
        case 'x': return 'Nevermind'
        case '+': return 'Tag this'
        case 'list': return 'Add to a list'
    }
    return '?'
}
function ajaxerror(obj, error_msg)
{
    obj.html(error_msg).show().delay(4000).fadeOut('slow')
}

function task_wait(task_id)
{
    if (task_id == "")
    {
        $.getJSON("/task_wait_error?task_id="+encodeURIComponent(task_id), function(data){});
        setTimeout('window.location.reload()', 200);
        return true;
    }
    setTimeout("window.location.reload()", 20000);
    $.ajax({
        url: "/task_wait/"+task_id,
        dataType: "json",
        type: "GET",
        timeout: 20000,
        success: function(data)
        {
            location.reload()
        },
        error: function(request, error)
        {
            //ajaxerror($("#wait_error"), 'There has been an error communicating with the server.<br><br>The error has been logged and we will try to fix it as soon as possible.<br><br>Will try refreshing in 4 seconds.')
            $.getJSON("/task_wait_error?task_id="+encodeURIComponent(task_id), function(data){});
            setTimeout('window.location.reload()', 4000);
        }
    })
}
function new_tag(tag_name)
{
    return $('<span class="tag"><a class="taglink" href="" tag_name="'+tag_name+'">'+tag_name+'</a></span>');
}
function taglink_dynamic()
{
    follow = 'follow'
    if (window.followed_tags && $.inArray($(this).text(), followed_tags) != -1)
    {
        follow = 'unfollow'
    }
    block = 'block'
    if ($(this).parent().hasClass('blocked_tag'))
    {
        block = 'unblock'
    }
    tag_name = $(this).attr('tag_name');
    action_url = dutils.urls.resolve('tag-action', { tag_name: tag_name });
    $(this).qtip(
    {
        content: '<span class="taglinks"><a href="'+action_url+'?action='+follow+'">'+follow+'</a><br /><a href="'+action_url+'?action='+block+'">'+block+'</a></span>',
        position: {
            corner: {
                target: 'bottomLeft'
            }
        },
        show: {
            solo: true
        },
        hide: {
            fixed: true
        }
    });
}
function generate_opinionbox_tips(){
    if (window.followed_tags)
    {
        $.each(followed_tags, function(i){
            $('a.taglink[tag_name="'+followed_tags[i]+'"]').parent().addClass("followed_tag");
        });
    }
    if (window.user_lists)
    {
        $("img.add_to_list").each(function(){$(this).qtip({
            content: "<div style='float: left' class='tip'>Add to:<br /><ul item_id='"+get_item_id($(this))+"'>"+user_lists+"</ul><span class='error'></span></div><img src='/media/images/ajax-loader.gif' class='nodisplay loading' style='float: right'>",
                position: {
                corner: {
                    target: 'topRight',
                    tooltip: 'bottomLeft'
                },
                adjust: {
                    screen: true
                }
            },
            show: {
                when: 'click',
                solo: true
            },
            hide: 'unfocus',
            style: {
                tip: true,
                border: {
                    width: 1,
                    radius: 5
                },
                name: 'light'
            }
                
        })}); 
    }
    else
    {
        $("img.add_to_list").remove();
    }
    $("a.addtag").click(function(e){
        tagbox = $("<input/>").attr("type", "text").attr('name', 'tag').addClass("tagbox");
        $(this).replaceWith(tagbox);
        tagbox.keypress(function(e){
            if (e.which == 44) { // comma
                $(this).parent().submit();
                e.preventDefault();
            }
        })
        .autocomplete({
			source: "/tagsearch",
			minLength: 2,
			select: function( event, ui ) {
                if (ui.item)
                {
                    $(this).parent().submit();
                }
			}
		});
        tagbox.wrap('<form class="tagthis" item_id="'+get_item_id(tagbox)+'" style="display: inline-block"/>');
        tagbox.after("<span class='error'></span><img src='/media/images/ajax-loader.gif' class='nodisplay loading' style='margin-right: 1em'>");
        tagbox.focus();
        e.preventDefault();
    });

    $('.tag a.taglink').each(taglink_dynamic);

}

$(document).ready(function(){
    $(".box").live("hover", 
        function(e){
            if (e.type == "mouseenter")
            {
                $(this).addClass('highlight')
            }
            else
            {
                $(this).removeClass('highlight')
                $(this).find('.add_to_list_outer').hide()
            }
        }
    )
    $(".user_rate .rating_small").live("hover", 
        function(e){
            if (e.type == "mouseenter")
            {
                $(this).removeClass('rate')
                seq_term = get_seq_term(this)
                rsh = $("#rsh_"+seq_term)
                rsh.html(rating_to_hint($(this)))
            }
            else {
                $(this).addClass('rate')
                seq_term = get_seq_term(this)
                rsh = $("#rsh_"+seq_term)
                rsh.html('')
            }
        }
    )
    $("form.tagthis").live("submit", function(e){
        $(this).children(".loading").show()
        item_id = $(this).attr('item_id')
        var self = this
        $.ajax({
            url: "/addtag/"+item_id,
            data: $(this).serialize(),
            dataType: "json",
            type: "GET",
            timeout: 2000,
            success: function(data)
            {
                $(self).children(".loading").hide()
                if (!data)
                {
                    /* this is due to a bug(?) in jQuery 1.4.2 */
                    ajaxerror($(self).children('.error'), 'Error: could not communicate with the server')
                    return;
                }
                if (data['success'])
                {
                    tagbox = $(self).children("input[name=tag]");
                    tag_name = tagbox.val();
                    tagbox.val('');
                    newtag = new_tag(tag_name);
                    $(self).after(newtag);
                    $(self).after(' ');
                    newtag.children('a.taglink').each(taglink_dynamic);
                    tagbox.autocomplete('close');
                    return;
                }
                else
                {
                    ajaxerror($(self).children('.error'), data['error_msg'])
                }
            },
            error: function(request, error)
            {
                $(self).children(".loading").hide()
                ajaxerror($(self).children('.error'), 'Error: could not communicate with the server')
            }
        })
        e.preventDefault();
    });
    $(".user_rate .rating_small:not(img)").live('click', function(e)
    {
        if ($(this).hasClass("rated"))
        {
            return false;
        }
        item_id = get_item_id(this)
        seq_term = get_seq_term(this)
        rating = $(this).html()
        ld = $("#ld_"+seq_term)
        opinion = $(this).parents(".opinion")
        if (rating == 'x')
        {
            ld.show()
            $.getJSON("/opinion/remove/"+item_id, function(data){
                opinion.hide('slow')
                ld.hide()
            })
        }
        else
        {
            var self = this
            ld.show()
            $.getJSON("/opinion/set/"+item_id+"/"+rating, function(data){
                ld.hide()
                $(self).siblings().removeClass("rated")
                $(self).addClass("rated")
                yr = $("#yr_"+seq_term)
                yr.removeClass("rating1 rating2 rating3 rating4 rating5 notrated")
                yr.addClass("rating"+rating)
                yr.html(rating).show()
                yr.parent().removeClass("nodisplay")
                if ($(self).parents(".click_hides").length)
                {
                    $(self).parent().hide()
                    opinion.hide('slow')
                    return true;
                }
                
                /* item profile */
                yr.siblings(".rating_verbose").html(rating_to_hint($(self)))
                yr.siblings(".user_opinion").children(".user_rate").children(".delete").show()
            })
        }
    })

    $('a.replylink').click(function(e){
        $(this).parent().parent().children('form.addcomment').show();
        e.preventDefault();
    });

    /* AJAX login forms */
    $("#loginform").submit(function(e)
    {
        $(this).children(".loading").show()
        var self = this
        $.ajax({
            url: "/account/login/ajax",
            dataType: "json",
            type: "POST",
            data: $(this).serialize(),
            timeout: 2000,
            success: function(data)
            {
                $(self).children(".loading").hide()
                if (!data)
                {
                    /* this is due to a bug(?) in jQuery 1.4.2 */
                    ajaxerror($("#loginform_error"), 'Error: could not communicate with the server')
                    return;
                }
                if (data['success'])
                {
                    src = "/"
                    if (next)
                    {
                        src = next
                    }
                    window.location.replace(src)
                }
                else
                {
                    ajaxerror($("#loginform_error"), data['error_msg'])
                }
            },
            error: function(request, error)
            {
                $(self).children(".loading").hide()
                ajaxerror($("#loginform_error"), 'Error: could not communicate with the server')
            }
        })
        e.preventDefault()
    })
    $("#signupform").submit(function(e)
    {
        id = $(this).attr("id")
        $(this).children(".loading").show()
        var self = this
        $.ajax({
            url: "/account/signup/ajax",
            dataType: "json",
            type: "POST",
            data: $(this).serialize(),
            timeout: 2000,
            success: function(data)
            {
                $(self).children(".loading").hide()
                if (!data)
                {
                    /* this is due to a bug(?) in jQuery 1.4.2 */
                    ajaxerror($("#signupform_error"), 'Error: could not communicate with the server')
                    return;
                }
                if (data['success'])
                {
                    $('#'+id).hide('fast')
                    $('#'+id+"_thankyou").show('fast') 
                    setTimeout('window.location.replace("/")', 2000)
                }
                else
                {
                    ajaxerror($('#'+id+"_error"), data['error_msg'])
                }
            },
            error: function(request, error)
            {
                $(self).children(".loading").hide()
                ajaxerror($("#"+id+"_error"), 'Error: could not communicate with the server')
            }
        })
        e.preventDefault()
    })

    $("form.addcomment").submit(function(e)
    {
        $(this).children(".loading").show()
        var self = this
        $.ajax({
            url: $(self).attr("action")+".json",
            dataType: "json",
            type: "POST",
            data: $(this).serialize(),
            timeout: 5000,
            success: function(data)
            {
                $(self).children(".loading").hide()
                if (!data)
                {
                    ajaxerror($(self).children(".error"), 'Error: could not communicate with the server')
                    return;
                }
                if (data['success'])
                {
                    $(self).siblings('.thankyou').show('fast') 
                    $(self).hide('fast')
                    setTimeout('window.location.replace("'+data['redirect_url']+'")', 2000)
                }
                else
                {
                    ajaxerror($(self).children(".error"), data['error_msg'])
                }
            },
            error: function(request, error)
            {
                $(self).children(".loading").hide()
                ajaxerror($(self).children(".error"), 'Error: could not communicate with the server')
            }
        })
        e.preventDefault()
    })

    /* search */
    if ($("#user_cats").length > 0)
    {
        /* user has categories */
        
        $("#global_cats").hide()
        $("#user_cats_more").click(function(e){
            $("#global_cats").show()
            $(this).parent().hide()
            e.preventDefault()
        })
    }

    /* show hide */
    $("a.showhide").click(function(e)
    {
        shown = $(this).parents(".show")
        hidden = shown.siblings(".hide")
        shown.removeClass('show').addClass('hide')
        hidden.removeClass('hide').addClass('show')
        e.preventDefault()  
    })

    /* textarea resizer */
    $(".resizable").resizable({handles: "s"});

    /* sortables */
    $(".sortable").sortable({
        stop: function(e, ui)
        {
            ui.item.removeClass("highlight");
        }
    });
    $(".sortable").disableSelection();

    /* editables */
    $(".editable:not(.noedit):not(.textarea)").append(editlink);
    $(".editable.textarea").append(textarealink);
    $(".editable:not(.noremove)").append(removelink);
    $(".editable > .remove").live("click", function(e)
    {
        $(this).parent().replaceWith("");
        e.preventDefault()
    })
    nl2br = function(s)
    {
        return s.replace(/\n\n/g, "<br /><br />");
    }
    $(".editable > .edit").live("click", function(e)
    {
        p = $(this).parent()
        type = $(this).attr('editable')
        if (type == 'textarea')
        {
            d = p.children('div')
            markdown = d.attr('markdown')
            p.html("<form><textarea name='field'>"+markdown+"</textarea><input type='submit' value='Edit'>"+textareaajax+"</form>");
        }
        else
        {
            p.html(p.getText())
            input = $("<input />").attr("type", "text").attr("name", "field").val(p.html());
            p.html(input);
            input.wrap("<form></form>");
        }
        p.children("form").submit(function(e)
        {
            if (type == 'textarea')
            {
                i = $(this).children("textarea")
                loading = $(this).children('.loading')
                unprocessed = i.val()
                loading.show()
                
                var self = this
                $.ajax({
                    url: "/utils/markdown",
                    dataType: "json",
                    type: "POST",
                    data: "text="+encodeURIComponent(unprocessed),
                    timeout: 2000,
                    success: function(data)
                    {
                        loading.hide()
                        if (data['success'])
                        {
                            result = "<div markdown='"+unprocessed.replace(/'/g, "&apos;")+"'>"+data['html']+"</div>";
                            $(self).replaceWith(result+textarealink+removelink)
                            return;
                        }
                        ajaxerror($(self).children('.error'), "Error: could not communicate with the server")
                        
                    },
                    error: function(request, error)
                    {
                        loading.hide()
                        ajaxerror($(self).children('.error'), "Error: could not communicate with the server")
                    }
                })

            }
            else
            {
                i = $(this).children("input")
                $(this).replaceWith(i.attr("value")+editlink+removelink)
            }
            e.preventDefault()
        })
        e.preventDefault()
    })

    update_add_select = function ()
    {
        val = $("#add_select").val()
        $("#list_add").removeClass("item text heading").addClass(val);
        if (val == 'item')
        {
            $("#add_submit").val(" ");
        }
        else
        {
            $("#add_submit").val("+");
        }
    }
    update_add_select();

    $("#add_select").change(function(e){
        update_add_select();
        e.preventDefault();
    });

    item_search = function(query, s, n)
    {
        $.getJSON("/search.json?q="+encodeURIComponent(query)+"&s="+s+"&n="+n, function(data){
            if (data.success)
            {
                is = $("#item_selector");
                is.html("");
                $.each(data.results, function(i, item)
                {
                    p = $("<p />");
                    $("<input />").attr("item_id", item.id).attr("item_name", item.name).attr("item_url", item.url).attr("type", "button").addClass("additem").val("+").click(function(e)
                    {
                        additem($(this).attr("item_id"), $(this).attr("item_name"), $(this).attr("item_url"), "", "");
                        e.preventDefault();
                    }).appendTo(p);
                    p.append(" ");
                    $("<a />").attr("href", item.url).text(item.name).appendTo(p);
                    $("<span />").addClass("smalltext").text(" "+item.category).appendTo(p);
                    p.appendTo(is);
                })
                pagination = $("<p />");
                pagination.wrap($("<div />").addClass("smalltext"));
                if (data.start > 0)
                {
                    $("<a />").attr("href", "#").text("< previous").click(function(e)
                    {
                        item_search(query, data.start-data.n, data.n);
                        e.preventDefault();
                    }).appendTo(pagination);
                    pagination.append("&nbsp;&nbsp;&nbsp;&nbsp;");
                }
                if (data.left > 0)
                {
                    $("<a />").attr("href", "#").text(data.left+" more results >").click(function(e)
                    {
                        item_search(query, data.start+data.n, data.n);
                        e.preventDefault();
                    }).appendTo(pagination);
                }
                pagination.appendTo(is);
            }
            else
            {
                ajaxerror($("#item_selector_error"), data.error);
            }
        })
    }

    $("#list_add").submit(function(e){
        type = $("#add_select").val();
        if (type == 'heading')
        {
            addheading($("#add_text").val(), true);
        }
        else if (type == 'text')
        {
            i = $("#add_textarea")
            loading = $(this).children('.loading')
            unprocessed = i.val()
            loading.show()
            
            var self = this
            $.ajax({
                url: "/utils/markdown",
                dataType: "json",
                type: "POST",
                data: "text="+encodeURIComponent(unprocessed),
                timeout: 2000,
                success: function(data)
                {
                    loading.hide()
                    if (data['success'])
                    {
                        addtext(unprocessed, data['html'], true);
                        return;
                    }
                    ajaxerror($(self).children('.error'), "Error: could not communicate with the server")
                    
                },
                error: function(request, error)
                {
                    loading.hide()
                    ajaxerror($(self).children('.error'), "Error: could not communicate with the server")
                }
            })
        }
        else if (type =='item')
        {
            v = $("#add_item").val();
    
            item_search(v, 0, 10);        
        }
        e.preventDefault();
    });

    $("#list_save").click(function(e)
    {
        $(this).siblings(".loading").show()
        var self = this
        $.ajax({
            url: "/list/save",
            dataType: "json",
            type: "POST",
            data: list_serialize(),
            timeout: 2000,
            success: function(data)
            {
                $(self).siblings(".loading").hide()
                if (!data)
                {
                    /* this is due to a bug(?) in jQuery 1.4.2 */
                    ajaxerror($("#list_save_error"), 'Error: could not communicate with the server')
                    return;
                }
                if (data['success'])
                {
                    ajaxerror($("#list_save_info"), 'List saved');
                    return;
                }
                else
                {
                    ajaxerror($("#list_save_error"), data['error_msg'])
                }
            },
            error: function(request, error)
            {
                $(self).siblings(".loading").hide()
                ajaxerror($("#list_save_error"), 'Error: could not communicate with the server')
            }
        })
        e.preventDefault();
    });

    $(".qtip ul a").live("click", function(e){
        
        $(this).parents('.tip').siblings(".loading").show()
        list_id = $(this).attr('list_id')
        item_id = $(this).parents('ul').attr('item_id')
        var self = this
        $.ajax({
            url: "/list/to/"+list_id+"/add/"+item_id,
            dataType: "json",
            type: "GET",
            timeout: 2000,
            success: function(data)
            {
                $(self).parents('.tip').siblings(".loading").hide()
                if (!data)
                {
                    /* this is due to a bug(?) in jQuery 1.4.2 */
                    ajaxerror($(self).parents('ul').siblings('.error'), 'Error: could not communicate with the server')
                    return;
                }
                if (data['success'])
                {
                    tooltip = $(self).parents('.qtip');
                    tooltip.qtip('api').elements.target.parents('.opinion.click_hides').hide('slow');
                    tooltip.qtip('hide');
                    return;
                }
                else
                {
                    ajaxerror($(self).parents('ul').siblings('.error'), data['error_msg'])
                }
            },
            error: function(request, error)
            {
                $(self).parents('.tip').siblings(".loading").hide()
                ajaxerror($(self).parents('ul').siblings('.error'), 'Error: could not communicate with the server')
            }
        })
        e.preventDefault();
    });

    $('button.also_liked').each(function(){
        $(this).qtip(
        {
            content: '<a class="also_liked" like_type="'+$(this).attr('like_type')+'" like_value="true">like</a><br><a class="also_liked" like_type="'+$(this).attr('like_type')+'" like_value="false">dislike</a><br>',
            position: {
                corner: {
                    target: 'bottomLeft'
                }
            },
            show: {
                when: 'click'
            },
            hide: 'unfocus'
        });
        $(this).hover(function(e){
            $(this).addClass("highlight");
        },function(e){
            $(this).removeClass("highlight");
        });
    });
    $('a.also_liked').live('click', (function(e){
        button = $('button.also_liked[like_type='+$(this).attr('like_type')+']');
        button.children('.like_dislike').html($(this).attr('like_value')=='true' ? 'like' : 'dislike');
        button.qtip('hide');
        like = $('button.also_liked[like_type=like] .like_dislike').html();
        also_like = $('button.also_liked[like_type=also_like] .like_dislike').html();
        $('#also_liked_also').html((like == also_like) ? 'also' : '');        
        ld = $("#ld_also_liked")
        ld.show();
        $.getJSON("/also_liked/"+$("#item").attr("item_id")+"/"+(like=='like')+"/"+(also_like=='like'), function(data){
            ld.hide();
            if (data.success)
            {
                $("div.also_liked").html(data.items);
                generate_opinionbox_tips();
            }
            else
            {
                ajaxerror($("#also_liked_error"), data.error);
            }
        })
    }));

    $('a.delete-confirm').click(function(e){
        $(this).parent().children('span.delete-confirm').fadeIn('slow');
        $(this).addClass("delete-clicked");
    });
    $('a.delete-undelete').click(function(e){
        $(this).parent().fadeOut('slow');
        $(this).parent().parent().children('a.delete-link').removeClass("delete-clicked");
        e.preventDefault();
    });
    $("ul.menu li").hover(function(e) {
        $(this).children('ul.submenu').show();
    },function(e){
        $(this).children('ul.submenu').hide();
    });

    /* users autocomplete */
    $("#users_autocomplete").autocomplete({
			source: "/usersearch",
			minLength: 2,
			select: function( event, ui ) {
                if (ui.item)
                {
                    window.location.replace(($(this).attr("url").replace(',,,', $(this).attr("usernames")+','+ui.item.value)));
                }
			}
		});

    /* tags autocomplete */
    $("input.tag_autocomplete").autocomplete({
			source: "/tagsearch",
			minLength: 2,
			select: function( event, ui ) {
                if (ui.item)
                {
                    enter_tag(ui.item.value);
                }
			}
		});
    /* search autocomplete */
    $("#search").autocomplete({

            source: function( request, response ) {
                $.getJSON( "/search/"+encodeURIComponent(this.term)+"*.autocomplete", response);
                
            },
            search: function() {
                var lastword = this.value.split(" ").pop();
                if ( lastword.length < 3 ) {
                    return false;
                }
            },
			select: function( event, ui ) {
                if (ui.item)
                {
                    window.location.replace(ui.item.url);
                }
			}
		})
        .data( "autocomplete" )._renderItem = function( ul, item ) {
            re = new RegExp("("+this.term.split(" ").join("|")+")", "ig");
            label = item.name.replace(re, "<b>$1</b>");
			return $( "<li></li>" )
				.data( "item.autocomplete", item )
				.append( "<a>" + label + "</a>" )
				.appendTo( ul );
		};

    /* rating graphs */
    $("#ratings_graph").qtip({
        content: "a",
        show: {when: false, effect: {length: 0}},
        position: {target: 'mouse', corner: {target: 'topMiddle', tooltip: 'bottomMiddle'}},
        hide: {effect: {length: 0}},
        style: {
            tip: true,
            border: {
                width: 1,
                radius: 5,
                color: '#b6dbf8'
            },
            name: 'light'
        }
    });
    $("#ratings_graph").bind("plothover", function (event, pos, item) {
        //alert("You hovered at " + pos.x + ", " + pos.y);
        // secondary axis coordinates if present are in pos.x2, pos.y2,
        // if you need global screen coordinates, they are pos.pageX, pos.pageY

        if (item) {

            if (previousPoint != item.datapoint) {
                previousPoint = item.datapoint;
                $(this).qtip("api").updateContent(item.datapoint[1]);
                $(this).qtip("show");
            }
        }
        else {
            previousPoint = null;
            $(this).qtip("hide");
        }
    });

    /* pagination */
    $('div.pagination button.more').live('click', function(e){
        loading = $("<img/>").attr("src", "/media/images/ajax-loader.gif").addClass("loading");
        href = $(this).attr("href") + '.json';
        $(this).replaceWith(loading);
        $.getJSON(href, function(data){
            loading.parent().replaceWith(data);
            generate_opinionbox_tips();
        });
        _gaq.push(['_setCustomVar',
             2,                   // This custom var is set to slot #1.  Required parameter.
             'Clicked more',      // The name acts as a kind of category for the user activity.  Required parameter.
             'Yes',               // This value of the custom variable.  Required parameter.
             3                    // Sets the scope to session-level.  Optional parameter.
          ]);
        
    });

    $("input#tagfilter").keyup(function(e){
        filter = $(this).val();
        if (filter.length >= 2)
        {
            $('div.tag-explorer div.tag-cell').hide();
            $('div.tag-explorer div.tag-cell[tag*='+filter+']').show();
        }
    });

    $("input.short_url").focus(function(e){
        this.select();
    })
    .mouseup(function(e){ // webkit fix
        e.preventDefault();
    });
            

});
