# urls.py
# defines all URL routes for the figure skating app, linking views to pages like skater detail,
# competition creation, program management, and element usage analysis

from django.urls import path
from django.conf import settings
from . import views
from .views import *

urlpatterns = [
    path(r'', HomeView.as_view(), name='home'),  
    # home page showing recent competitions and top skaters

    path('skaters/', ShowAllSkaters.as_view(), name='skaters_list'),
    # view all skaters (paginated)

    path('competition/create/', CreateCompetitionView.as_view(), name='create_competition'),
    # create a new competition (step 1)

    path('skater/<int:pk>/', SkaterDetailView.as_view(), name='skater_detail'),
    # view a specific skater's profile and programs

    path('competitions', ShowAllCompetitions.as_view(), name="show_all_comps"),
    # view all competitions

    path('programs/', ShowAllPrograms.as_view(), name="show_all_programs"),
    # view all competitions

    path('competitions/<int:pk>/', CompetitionDetailView.as_view(), name='competition_detail'),
    # competition results and breakdown

    path('competition/create/select_programs/', SelectProgramsView.as_view(), name='select_programs'),
    # assign programs to skaters for a competition (step 2)

    path('program/<int:pk>/', ProgramDetailView.as_view(), name='program_detail'),
    # view program details, including elements, base values, and comp history for that program

    path('program/create/', CreateProgramView.as_view(), name='create_program'),
    # create a new program (skater selected from form)

    path('skater/<int:pk>/program/create/', views.CreateProgramView.as_view(), name='create_program_for_skater'),
    # create a program for a specific skater (ID from URL)

    path('skater/<int:pk>/update/', UpdateSkaterView.as_view(), name='update_skater'),
    # update skater info (nationality, skating club, and image)

    path('competition/<int:pk>/delete/', CompetitionDeleteView.as_view(), name='delete_competition'),
    # delete a competition

    path('elements/', views.ElementListView.as_view(), name='element_list'),
    # list of all elements with search/filter

    path('elements/<int:pk>/', views.ElementUsageView.as_view(), name='element_usage_report'),
    # report showing where and how an element has been used
]