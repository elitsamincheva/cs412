# restaurant/views.py
# ------------------------------------------------------------------------------
# This file contains views for a simple restaurant ordering system.
# 
# The views include:
# 1. `main`: Displays the restaurant's main page.
# 2. `order`: Shows the order form with menu items and a randomly selected daily special.
# 3. `confirmation`: Displays the order confirmation with selected items, customer info,
#    and a randomly generated ready time for the order.
#
# The views make use of Django templates to display the content and random selections 
# for the daily special and ready time.
# ------------------------------------------------------------------------------

import random
from django.shortcuts import render
from datetime import datetime, timedelta


def main(request):
    """display information about the restaurant"""
    template_name = "restaurant/main.html"
    return render(request, template_name)


def order(request):
    """display the order form with menu items and a randomly selected daily special"""
    template_name = "restaurant/order.html"

    # regular menu items
    menu_items = [
        {
            "name": "French Toast KING",
            "price": 18.75,
            "image": "https://popmenucloud.com/cdn-cgi/image/width%3D2400%2Cheight%3D2400%2Cfit%3Dscale-down%2Cformat%3Dauto%2Cquality%3D60/lzaqjwcu/e5377eb4-5c49-4003-a4ac-140db363480c.jpg",
            "value": "frenchtoast",
            "toppings": []
        },
        {
            "name": "Sunrise Pizza",
            "price": 16.50,
            "image": "https://popmenucloud.com/cdn-cgi/image/width%3D2400%2Cheight%3D2400%2Cfit%3Dscale-down%2Cformat%3Dauto%2Cquality%3D60/lzaqjwcu/21a0c2b3-c7de-4618-bf2d-970206273702.jpg",
            "value": "pizza",
            "toppings": []
        },
        {
            "name": "Urth Spanish Latte",
            "price": 6.75,
            "image": "https://popmenucloud.com/cdn-cgi/image/width%3D2400%2Cheight%3D2400%2Cfit%3Dscale-down%2Cformat%3Dauto%2Cquality%3D60/lzaqjwcu/37a59a8d-0837-4445-b37d-ee3e72b5f6c7.jpg",
            "value": "coffee",
            "toppings": []
        },
        {
            "name": "The Tostada",
            "price": 18.75,
            "image": "https://popmenucloud.com/cdn-cgi/image/width%3D3840%2Cheight%3D3840%2Cfit%3Dscale-down%2Cformat%3Dauto%2Cquality%3D60/lzaqjwcu/fea20b00-2a7f-419f-835b-3164e59167e9.jpg",
            "value": "tostada",
            "toppings": []
        },
        {
            "name": "The Mushroom Omelet",
            "price": 15.50,
            "image": "https://popmenucloud.com/cdn-cgi/image/width%3D2400%2Cheight%3D2400%2Cfit%3Dscale-down%2Cformat%3Dauto%2Cquality%3D60/lzaqjwcu/73e0edc3-413f-499a-b1a6-df940dbb7c60.jpg",
            "value": "omelet",
            "toppings": [
                {"name": "Add Avocado", "price": 3.75, "value": "avocado"},
                {"name": "Add Spicy Sausage", "price": 5.95, "value": "sausage"},
                {"name": "Egg Whites Only", "price": 2.50, "value": "egg_whites"}
            ]
        }
    ]

    # daily specials
    daily_specials = [
        {
            "name": "Stuffed French Toast",
            "price": 20.75,
            "image": "https://popmenucloud.com/cdn-cgi/image/width%3D3840%2Cheight%3D3840%2Cfit%3Dscale-down%2Cformat%3Dauto%2Cquality%3D60/lzaqjwcu/9ad425b6-a948-4ad8-ae62-9484fd9bbd86.jpg"
        },
        {
            "name": "Eggs Benedict Canyon with Smoked Salmon",
            "price": 19.75,
            "image": "https://popmenucloud.com/cdn-cgi/image/width%3D3840%2Cheight%3D3840%2Cfit%3Dscale-down%2Cformat%3Dauto%2Cquality%3D60/lzaqjwcu/74701200-602d-4d2c-9142-b2085fd63b76.jpg"
        },
        {
            "name": "Parma Panini",
            "price": 18.75,
            "image": "https://popmenucloud.com/cdn-cgi/image/width%3D3840%2Cheight%3D3840%2Cfit%3Dscale-down%2Cformat%3Dauto%2Cquality%3D60/lzaqjwcu/b2ad3621-267f-4b74-aa8d-220146d8e5e9.jpg"
        },
        {
            "name": "Pumpkin Pie (with Whipped Cream)",
            "price": 9.75,
            "image": "https://popmenucloud.com/cdn-cgi/image/width%3D3840%2Cheight%3D3840%2Cfit%3Dscale-down%2Cformat%3Dauto%2Cquality%3D60/lzaqjwcu/917ffc16-e08c-4fba-b94c-99614b5a6d5c.jpg"
        }
    ]

    # choose a random daily special
    daily_special = random.choice(daily_specials)

    context = {
        "menu_items": menu_items,
        "daily_special": daily_special
    }

    return render(request, template_name, context)




def confirmation(request):
    """Display the order confirmation page"""

    template_name = "restaurant/confirmation.html"  

    if request.POST:  
        selected_items = []  # store the selected menu items
        total_price = 0  # keep track of the total price

        for key in request.POST.getlist("item"):  # iterate through each selected menu item
            item_name, item_price = key.split("|")  # split the value into item name and price
            item_price = float(item_price)  
            selected_items.append({"name": item_name, "price": item_price})  
            total_price += item_price  

        # process selected extra toppings
        selected_toppings = []  # store the selected toppings
        for key in request.POST:  # iterate through the POST data to check for toppings
            if key.startswith("topping_"): 
               
                topping_name, topping_price = request.POST[key].split("|")  # split topping name and price
                topping_price = float(topping_price)  
                selected_toppings.append({"name": topping_name, "price": topping_price})  
                total_price += topping_price 

        # get daily special (if it is ordered)
        daily_special_name = request.POST.get("item_special") 
        daily_special_price = float(request.POST.get("item_special_price", 0))  

        if daily_special_name:  
            selected_items.append({"name": daily_special_name, "price": daily_special_price})  
            total_price += daily_special_price  

        # Get all the customer info
        customer_info = {
            "name": request.POST.get("name", ""), 
            "phone": request.POST.get("phone", ""), 
            "email": request.POST.get("email", ""), 
            "special_instructions": request.POST.get("special_instructions", ""), 
        }

        # generating the random ready time between 30 and 60 minutes
        minutes_until_ready = random.randint(30, 60) 
        print(datetime.now())
        ready_time = datetime.now() + timedelta(minutes=minutes_until_ready) 
        ready_time_formatted = ready_time.strftime("%I:%M %p")  

        context = {
            "selected_items": selected_items, 
            "selected_toppings": selected_toppings, 
            "customer_info": customer_info, 
            "total_price": total_price,  
            "ready_time": ready_time_formatted,  
        }


        return render(request, template_name, context)

    # if the request is not a POST (initial page load), render the order page
    return render(request, "restaurant/order.html")

