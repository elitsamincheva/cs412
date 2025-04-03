# urls.py
# this file contains the url patterns for the voter analytics app
# each path links to a view that handles different functionality:
# - the root url displays a list of voters
# - the 'voter' url shows details for a specific voter
# - the 'graphs' url shows various graphs related to voter data

from django.urls import path
from .views import *

urlpatterns = [
    path('', VoterListView.as_view(), name='voters'),   # root url serves voter list
    path('voter/<int:pk>/', VoterDetailView.as_view(), name='voter'),   # voter details for a specific voter
    path('graphs/', GraphsView.as_view(), name='graphs'),   # displays voter-related graphs
]
