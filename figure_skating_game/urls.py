from django.urls import path
from django.conf import settings
from . import views
from .views import *

urlpatterns = [
    # Root URL: 
    path(r'', ShowAllCompetitions.as_view(), name="show_all_comps"),
    path('skaters/', ShowAllSkaters.as_view(), name='skaters_list'),
    path('competition/create/', CreateCompetitionView.as_view(), name='create_competition'),
    path('skater/<int:pk>/', SkaterDetailView.as_view(), name='skater_detail'),
]

