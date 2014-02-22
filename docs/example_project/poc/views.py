from django.http import HttpResponse
from phantom_pdf import render_to_pdf


def home(request):
    if request.GET.get("print", None) == "pdf":
        return render_to_pdf(request, 'frula')
    else:
        return HttpResponse("Hello World!")
