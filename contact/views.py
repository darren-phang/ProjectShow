from django.shortcuts import render
from .models import ConcatMessage
# Create your views here.


def index(request):
    return render(request, "contact/contact.html")


def send_message(request):
    if request.method == "POST":
        message = ConcatMessage(
            name=request.POST['name'],
            email=request.POST['email'],
            subject=request.POST['subject'],
            message=request.POST['message']
        )
        message.save()
    return render(request, "contact/contact.html")
