from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import random



# lists for quotes and images
quotes = [
    "I am no longer accepting the things I cannot change. I am changing the things I cannot accept.",
    "Radical simply means \"grasping things at the root.\"",
    "You have to act as if it were possible to radically transform the world. And you have to do it all the time.",
    "We have to talk about liberating minds as well as liberating society.",
    "The idea of freedom is inspiring. But what does it mean? If you are free in a political sense but have no food, what's that? The freedom to starve?",
    "We live in a society of an imposed forgetfulness, a society that depends on public amnesia.",
    "It is in collectivities that we find reservoirs of hope and optimism.",
    "Movements are most powerful when they begin to affect the vision and perspective of those who do not necessarily associate themselves with those movements.",
    "We are never assured of justice without a fight."
]

images = [
    "https://info.umkc.edu/womenc/wp-content/uploads/2018/02/z.jpg",
    "https://speakout-website.s3.amazonaws.com/medium_Angela_Davis_5feb24c5b9.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Angela_Davis_in_a_half-length_portrait_by_Bernard_Gotfryd_-_crop.jpg/220px-Angela_Davis_in_a_half-length_portrait_by_Bernard_Gotfryd_-_crop.jpg",
    "https://assets.editorial.aetnd.com/uploads/2009/11/angela-davis-at-first-news-conference.jpg",
    "https://hips.hearstapps.com/hmg-prod/images/gettyimages-1286489423.jpg?crop=1xw:1.0xh;center,top&resize=640:*",
    "https://api.time.com/wp-content/uploads/2020/09/time-100-Angela-Davis.jpg",
    "https://cdn.britannica.com/24/7924-004-EC7DF3EB/Angela-Davis-1974.jpg",
    "https://whc.yale.edu/sites/default/files/event-images/angela_davis_pic_cropped.jpg",
    "https://cdn.artphotolimited.com/images/60913d60bd40b85323893a87/300x300/angela-davis-a-berlin-est-1973.jpg"
]

# views

def quote(request):
    """view for the main page displaying one random quote and image"""

    template_name = "quotes/quote.html"
    context = {
        "quote": random.choice(quotes),
        "image": random.choice(images)
    }
    return render(request, template_name, context)

def show_all(request):
    """display all quotes and images"""
    
    template_name = "quotes/show_all.html"
    
    # Pair quotes and images safely (zip stops at the shorter length)
    quote_image_pairs = list(zip(quotes, images))  

    context = {
        "quote_image_pairs": quote_image_pairs
    }
    
    return render(request, template_name, context)



def about(request):
    """Display information about Angela Davis and the creator."""
    famous_person = {
        "name": "Angela Davis",
        "bio": "Angela Davis is a political activist, scholar, and author known for her work in civil rights, prison abolition, and Black feminism. She was a prominent member of the Communist Party USA and was associated with the Black Panther Party.",
        "notable_work": "Are Prisons Obsolete?, Women, Race & Class",
        "birth_year": 1944,
    }

    creator_info = {
        "name": "Elitsa Mincheva",
        "bio": "Elitsa is a computer science student passionate about web development and data science. This web application was created as part of a project exploring Django and web frameworks.",
    }

    template_name = "quotes/about.html"
    return render(request, template_name, {"famous_person": famous_person, "creator_info": creator_info})



    
