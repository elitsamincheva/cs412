from django.urls import path
from .views import VoterListView

urlpatterns = [
    path('', VoterListView.as_view(), name='voters'),  # Root URL serves voter list
]
