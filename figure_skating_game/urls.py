from django.urls import path
from django.conf import settings
from . import views
from .views import *

urlpatterns = [
    path(r'', HomeView.as_view(), name='home'),  
    # home page showing recent comps and top skaters

    path('skaters/', ShowAllSkaters.as_view(), name='skaters_list'),
    # page showing all skaters (paginated)

    path('competition/create/', CreateCompetitionView.as_view(), name='create_competition'),
    # form to create a new competition

    path('skater/<int:pk>/', SkaterDetailView.as_view(), name='skater_detail'),
    # page showing details about one skater

    path('competitions', ShowAllCompetitions.as_view(), name="show_all_comps"),
    # page showing all competitions (paginated)

    path('programs/', ShowAllPrograms.as_view(), name="show_all_programs"),
    # page showing all programs (paginated)

    path('competitions/<int:pk>/', CompetitionDetailView.as_view(), name='competition_detail'),
    # detail page for one competition with its results

    path('competition/create/select_programs/', SelectProgramsView.as_view(), name='select_programs'),
    # view to pick programs for each skater after creating a comp

    path('program/<int:pk>/', ProgramDetailView.as_view(), name='program_detail'),
    # detail page for a program, showing its elements and executions

    path('program/create/', CreateProgramView.as_view(), name='create_program'),
    # form to create a new program (skater is selected in form)

    path('skater/<int:pk>/program/create/', views.CreateProgramView.as_view(), name='create_program_for_skater'),
    # form to create a new program already linked to a specific skater

    path('skater/<int:pk>/update/', UpdateSkaterView.as_view(), name='update_skater'),
    # modify existing skater data

    path('competition/<int:pk>/delete/', CompetitionDeleteView.as_view(), name='delete_competition'),
    # delete a competition

    path('elements/', views.ElementListView.as_view(), name='element_list'),
    path('elements/<int:pk>/', views.ElementUsageView.as_view(), name='element_usage_report'),

]