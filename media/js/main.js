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
})(jQuery); 
function get_item_id(self)
{
    item_id = $(self).parents(".user_opinion").attr("item")
    return item_id
}
function rating_to_hint(r)
{
    switch (r)
    {
        case '1': return 'Hate it'
        case '2': return 'Dislike it'
        case '3': return 'Neutral to it'
        case '4': return 'Like it'
        case '5': return 'Love it'
        case 'x': return 'Delete this opinion'
    }
    return '?'
}
function ajaxerror(obj, error_msg)
{
    obj.html(error_msg).show().delay(4000).fadeOut('slow')
}
$(document).ready(function(){
    $(".box").hover(
        function(e){
            $(this).addClass('highlight')
        },
        function(e){
            $(this).removeClass('highlight')
        }
    )
    $(".user_rate .rating_small").hover(
        function(e){
            $(this).removeClass('rate')
            item_id = get_item_id(this)
            rsh = $("#rsh_"+item_id)
            rsh.html(rating_to_hint($(this).html()))
        },
        function(e){
            $(this).addClass('rate')
            item_id = get_item_id(this)
            rsh = $("#rsh_"+item_id)
            rsh.html('')
        }
    )
    $(".user_rate .rating_small").mousedown(function(e)
    {
        if ($(this).hasClass("rated"))
        {
            return false;
        }
        item_id = get_item_id(this)
        rating = $(this).html()
        ld = $("#ld_"+item_id)
        ld.show()
        opinion = $(this).parents(".opinion")
        if (rating == 'x')
        {
            $.getJSON("/opinion/remove/"+item_id, function(data){
                opinion.hide('slow')
                ld.hide()
            })
        }
        else
        {
            var self = this
            $.getJSON("/opinion/set/"+item_id+"/"+rating, function(data){
                ld.hide()
                $(self).siblings().removeClass("rated")
                $(self).addClass("rated")
                yr = $("#yr_"+item_id)
                yr.removeClass("rating1 rating2 rating3 rating4 rating5")
                yr.addClass("rating"+rating)
                yr.html(rating).show()
                yr.parent().removeClass("nodisplay")
                if ($(self).parents(".terse").length)
                {
                    $(self).parent().hide()
                    opinion.hide('slow')
                    return true;
                }
                
                /* item profile */
                yr.siblings(".rating_verbose").html(rating_to_hint(rating))
                yr.siblings(".user_opinion").children(".user_rate").children(".delete").show()
            })
        }
    })


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

});

