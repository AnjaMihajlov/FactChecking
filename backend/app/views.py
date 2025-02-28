import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect

def home(request):
    return render(request,"homePage.html")

def about(request):
    return render(request,"about.html")

def factCheckHome(request):
    return render(request,"factCheckHome.html")

def factCheckResults(request):
    return render(request,"factCheckResults.html")

def consistencyCheckHome(request):
    return render(request,"consistencyCheckHome.html")

def consistencyCheckResults(request):
    return render(request,"consistencyCheckResults.html")

def uploadFile(request):
    if request.method == 'POST' and request.FILES:
        uploaded_file = request.FILES['fileInput']                           # 'fileInput' je name u formi
        fs = FileSystemStorage(location=settings.MEDIA_ROOT+"/uploads")
        filename = fs.save(uploaded_file.name, uploaded_file)

        return redirect('fcResults')

    return render(request, 'factCheckHome.html')
