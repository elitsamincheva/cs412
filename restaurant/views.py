from django.shortcuts import render


def main(request):
    """Display information about the restaurant"""
    template_name = "restaurant/main.html"
    return render(request, template_name)

def order(request):
    template_name = "restaurant/order.html"
    return render(request, template_name)

def confirmation(request):
    template_name = "restaurant/confirmation.html"
    return render(request, template_name)