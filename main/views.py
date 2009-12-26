from django.shortcuts import render_to_response

def welcome(request):
    if request.user.is_authenticated():
        return render_to_response("main/welcome.html")
    else:
        return render_to_response("main/welcome_anonymous.html")
