import random
from django.shortcuts import render

def main(request):
    """Display information about the restaurant"""
    template_name = "restaurant/main.html"
    return render(request, template_name)


def order(request):
    """Display the order form with menu items and a randomly selected daily special"""
    template_name = "restaurant/order.html"

    # menu items
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

    if request.method == "POST":
        selected_items = []
        total_price = 0

        # Process selected items
        for key in request.POST.getlist("item"): 
            item_name, item_price = key.split("|")
            item_price = float(item_price)
            selected_items.append({"name": item_name, "price": item_price})
            total_price += item_price

        # Process selected toppings
        selected_toppings = []
        for key in request.POST:
            if key.startswith("topping_"):
               
                topping_name, topping_price = request.POST[key].split("|")
                topping_price = float(item_price)
                selected_toppings.append({"name": topping_name, "price": topping_price})
                total_price += topping_price


        # Get daily special (if any)
        daily_special_name = request.POST.get("item_special")
        daily_special_price = float(request.POST.get("item_special_price", 0))

        if daily_special_name:
            selected_items.append({"name": daily_special_name, "price": daily_special_price})
            total_price += daily_special_price

        print(selected_toppings)

        # Get customer info
        customer_info = {
            "name": request.POST.get("name", ""),
            "phone": request.POST.get("phone", ""),
            "email": request.POST.get("email", ""),
            "special_instructions": request.POST.get("special_instructions", ""),
        }

        context = {
            "selected_items": selected_items,
            "selected_toppings": selected_toppings,
            "customer_info": customer_info,
            "total_price": total_price,
        }

        return render(request, template_name, context)

    # If accessed via GET, redirect to the order page
    return render(request, "restaurant/order.html")
