from django.shortcuts import render


def index(request):
    return render(request, "index.html", {"user_agent": request.user_agent})


def template_tags(request):
    return render(request, "template_tags.html", {"request": request})
