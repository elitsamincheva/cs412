from django.urls import path
from .views import *

urlpatterns = [
    path('', VoterListView.as_view(), name='voters'),  # Root URL serves voter list
    path('voter/<int:pk>/', VoterDetailView.as_view(), name='voter'),
    path('graphs/', GraphsView.as_view(), name='graphs'),
]
