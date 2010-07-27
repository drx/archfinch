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
    $(".user_rate .rating_small").click(function(e)
    {
        if ($(this).hasClass("rated"))
        {
            return false;
        }
        item_id = get_item_id(this)
        rating = $(this).html()
        if (rating == 'x')
        {
            opinion = $(this).parents(".opinion")
            $.getJSON("/opinion/remove/"+item_id, function(data){
                opinion.hide('slow')
            })
        }
        else
        {
            $.getJSON("/opinion/set/"+item_id+"/"+rating)
            $(this).siblings().removeClass("rated")
            $(this).addClass("rated")
            yr = $("#yr_"+item_id)
            yr.removeClass("rating1 rating2 rating3 rating4 rating5")
            yr.addClass("rating"+rating)
            yr.html(rating)
            yr.parent().removeClass("nodisplay")
        }
    })
    $("#menu_login").click(function(e)
    {
        $("#loginform").toggle('fast')
        $("#signupform").hide('fast')
        e.preventDefault()
    })
    $("#menu_signup").click(function(e)
    {
        $("#signupform").toggle('fast')
        $("#loginform").hide('fast')
        e.preventDefault()
    })
    $("#loginform").submit(function(e)
    {
        $(this).children(".loading").show()
        self = this
        $.ajax({
            url: "/account/login/ajax",
            dataType: "json",
            type: "POST",
            data: $(this).serialize(),
            success: function(data)
            {
                $(self).children(".loading").hide()
                if (data['success'])
                {
                    window.location.replace("/")
                }
                else
                {
                    $("#loginform_error").html(data['error_msg']).show().delay(2000).fadeOut('slow')
                }
            }
        })
        e.preventDefault()
    })
    $("#signupform").submit(function(e)
    {
        $(this).children(".loading").show()
        self = this
        $.ajax({
            url: "/account/signup/ajax",
            dataType: "json",
            type: "POST",
            data: $(this).serialize(),
            success: function(data)
            {
                $(self).children(".loading").hide()
                if (data['success'])
                {
                    window.location.replace("/")
                }
                else
                {
                    $("#signupform_error").html(data['error_msg']).show().delay(2000).fadeOut('slow')
                }
            }
            /* TODO: error */
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
});

