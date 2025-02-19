from django.shortcuts import render

# Create your views here.
def main(request):
    """display information about the restaurant"""
    template_name = "mini_fb/main.html"
    return render(request, template_name)