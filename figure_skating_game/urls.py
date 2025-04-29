from django.urls import path
from django.conf import settings
from . import views
from .views import *

urlpatterns = [
    # Root URL:
    path(r'', HomeView.as_view(), name='home'),
    path('skaters/', ShowAllSkaters.as_view(), name='skaters_list'),
    path('competition/create/', CreateCompetitionView.as_view(), name='create_competition'),
    path('skater/<int:pk>/', SkaterDetailView.as_view(), name='skater_detail'),
    path('competitions', ShowAllCompetitions.as_view(), name="show_all_comps"),
    path('programs/', ShowAllPrograms.as_view(), name="show_all_programs"),
    path('competitions/<int:pk>/', CompetitionDetailView.as_view(), name='competition_detail'),
    path('competition/create/select_programs/', SelectProgramsView.as_view(), name='select_programs'),
  
]