# views.py

# This file contains the views for the voter analytics application which include:
# 1. VoterListView: list view to display a paginated list of voters with filters for party affiliation, date of birth range, voter score, and election participation
# 2. VoterDetailView: detail view for displaying individual voter information
# 3. GraphsView: list view for displaying various voter analytics graphs:
#    - voter distribution by year of birth (bar chart)
#    - voter distribution by party affiliation (pie chart)
#    - voter participation in elections (histogram)

# the views utilize django generic views (ListView, DetailView) and Plotly for generating the charts
# context data is dynamically generated based on query parameters and voter data from the database

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Voter
from django.db.models import Min, Max
from datetime import datetime
import plotly
import plotly.graph_objects as go
import plotly.express as px
from django.utils.safestring import mark_safe
import pandas as pd

class VoterListView(ListView):
    """
    view for displaying a paginated list of voters with filtering options based on query parameters

    filters available:
    - party affiliation
    - minimum and maximum DOB
    - voter score
    - participation in specific elections

    The view retrieves a list of voters, applies the filters based on GET request parameters, 
    and renders the result in a paginated list
    """
    model = Voter
    template_name = "voters/voter_list.html"
    context_object_name = "voters"
    paginate_by = 100  #show 100 records per page

    def get_queryset(self):
        """
        Filters the voters based on query parameters from the request
        
        The filters include party affiliation, date of birth range (min/max), 
        voter score, and election participation. Each filter corresponds to 
        a specific GET parameter
        
        Returns:
            queryset: A filtered queryset of Voter objects
        """
        queryset = Voter.objects.all()

        # party affiliation filter
        party_filter = self.request.GET.get("party")
        if party_filter:
            queryset = queryset.filter(party=party_filter)

        # minimum date of birth filter
        min_dob_filter = self.request.GET.get("min_dob")
        if min_dob_filter:
            try:
                min_dob_date = datetime.strptime(min_dob_filter, '%Y').date()
                queryset = queryset.filter(dob__gte=min_dob_date)
            except ValueError:
                pass  # invalid date format, ignore filter

        # maximum date of birth filter
        max_dob_filter = self.request.GET.get("max_dob")
        if max_dob_filter:
            try:
                # assume max_dob is a year and set it to the last day of the year (12-31)
                max_dob_date = datetime.strptime(max_dob_filter, '%Y').date().replace(month=12, day=31)
                queryset = queryset.filter(dob__lte=max_dob_date)
            except ValueError:
                pass  # invalid date format, ignore filter
        # voter score filter
        voter_score_filter = self.request.GET.get("voter_score")
        if voter_score_filter:
            queryset = queryset.filter(voter_score=voter_score_filter)

        # election participation filter (check multiple elections)
        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        for election in elections:
            if self.request.GET.get(election):
                queryset = queryset.filter(**{election: True})

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds additional context for filtering options to the template context
        
        includes:
        - list of distinct party affiliations
        - minimum and maximum birth years available in the dataset
        - list of available years for filtering by DOB
        - list of elections for filtering voter participation
        
        Returns:
            context: A dictionary containing the context data for rendering the template
        """
        context = super().get_context_data(**kwargs)

        # get the available party affiliations
        parties = Voter.objects.values_list('party', flat=True).distinct()

        # get the minimum and maximum birth years from the dataset
        min_birth_year = Voter.objects.aggregate(Min('dob'))['dob__min'].year
        max_birth_year = Voter.objects.aggregate(Max('dob'))['dob__max'].year

        # create a list of years from min to max birth years
        years = list(range(min_birth_year, max_birth_year + 1))

        context['parties'] = parties
        context['min_birth_year'] = min_birth_year
        context['max_birth_year'] = max_birth_year
        context['years'] = years
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']

        return context
    

class VoterDetailView(DetailView):
    """
    view that displays the details of a single voter

    This view retrieves a specific Voter object from the database and renders
    its detailed information in a template. The template is expected to display
    the voter's personal details
    """
    model = Voter
    template_name = 'voter_analytics/voter_detail.html' 
    context_object_name = 'voter' 


class GraphsView(ListView):
    """
    view that generates various graphs related to voter data:
    - voter distribution by year of birth (bar chart)
    - voter distribution by party affiliation (pie chart)
    - voter participation in elections (histogram)
    
    filters can be applied to the voter data, such as party affiliation, date of birth, 
    voter score, and election participation
    """
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'

    def get_queryset(self):
        """
        returns a queryset of voters filtered based on query parameters (if provided)
        
        can filter by:
        - party affiliation
        - minimum and maximum date of birth
        - voter score
        - election participation
        
        Returns:
            queryset: A filtered queryset of voters.
        """
        # start with all voters
        queryset = Voter.objects.all()

        # filter voters by party affiliation if provided
        party_filter = self.request.GET.get("party")
        if party_filter:
            queryset = queryset.filter(party=party_filter)

        # filter voters by minimum date of birth if provided
        min_dob_filter = self.request.GET.get("min_dob")
        if min_dob_filter:
            try:
                min_dob_date = datetime.strptime(min_dob_filter, '%Y').date()
                queryset = queryset.filter(dob__gte=min_dob_date)
            except ValueError:
                pass  # invalid date format, just ignore it

        # filter voters by maximum date of birth if provided
        max_dob_filter = self.request.GET.get("max_dob")
        if max_dob_filter:
            try:
                max_dob_date = datetime.strptime(max_dob_filter, '%Y').date().replace(month=12, day=31)
                queryset = queryset.filter(dob__lte=max_dob_date)
            except ValueError:
                pass  # invalid date format, just ignore it

        # filter voters by voter score if provided
        voter_score_filter = self.request.GET.get("voter_score")
        if voter_score_filter:
            queryset = queryset.filter(voter_score=voter_score_filter)

        # filter voters by election participation if provided
        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        for election in elections:
            if self.request.GET.get(election):
                queryset = queryset.filter(**{election: True})

        return queryset

    def get_context_data(self, **kwargs):
        """
        adds additional context to the template, including:
        - party affiliations
        - min/max birth years
        - available years for birth dates
        - election names for filtering
        - graphs for voter distribution by birth year, party, and election participation
    
        Returns:
            context: A dictionary of context data to be used in the template.
        """
        context = super().get_context_data(**kwargs)

        # get all available party affiliations
        parties = Voter.objects.values_list('party', flat=True).distinct()

        # get the minimum and maximum birth years from the voters
        min_birth_year = Voter.objects.aggregate(Min('dob'))['dob__min'].year
        max_birth_year = Voter.objects.aggregate(Max('dob'))['dob__max'].year

        # create a list of all years between the min and max birth years
        years = list(range(min_birth_year, max_birth_year + 1))

        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']

        context['parties'] = parties
        context['min_birth_year'] = min_birth_year
        context['max_birth_year'] = max_birth_year
        context['years'] = years
        context['elections'] = elections

        # --- voter distribution by year of birth (bar chart) ---
        birth_years = self.get_queryset().values_list('dob', flat=True)
        birth_years = [dob.year for dob in birth_years if dob]  # extract years from birth dates

        if birth_years:
            # creating a DataFrame from the birth years
            df_years = pd.DataFrame({'year': birth_years})
            birth_year_counts = df_years['year'].value_counts().reset_index()
            birth_year_counts.columns = ['year', 'count']
            birth_year_counts = birth_year_counts.sort_values(by='year')  # sort by year

            # creating the bar chart
            fig_bar = px.bar(
                birth_year_counts,
                x='year', 
                y='count', 
                title="Voter Distribution by Year of Birth",
                labels={'year': 'Year of Birth', 'count': 'Count'}
            )

            # adding the bar chart to the context
            context['birth_year_graph'] = mark_safe(fig_bar.to_html(full_html=False))
        else:
            context['birth_year_graph'] = "<p>No data available.</p>"

        # --- voter distribution by party affiliation (pie chart) ---
        parties = self.get_queryset().values_list('party', flat=True)
        parties = [p for p in parties if p]  

        if parties:
            # creating a DataFrame for party data
            df_parties = pd.DataFrame({'party': parties})
            party_counts = df_parties['party'].value_counts().reset_index()
            party_counts.columns = ['party', 'count']

            # creating the pie chart
            fig_pie = px.pie(
                party_counts,
                names='party', 
                values='count', 
                title="Voter Distribution by Party Affiliation",
                width=900,  
                height=700  
            )

            # adding the pie chart to the context
            context['party_pie_chart'] = mark_safe(fig_pie.to_html(full_html=False))
        else:
            context['party_pie_chart'] = "<p>No data available.</p>"

        # --- voter participation in elections (histogram) ---
        # counting how many voters participated in each election
        election_counts = {election: self.get_queryset().filter(**{election: True}).count() for election in elections}

        if any(election_counts.values()):  # check if there's any participation data
            # creating a DataFrame for election participation data
            df_elections = pd.DataFrame(list(election_counts.items()), columns=['Election', 'Count'])

            # creating the histogram
            fig_hist = px.bar(
                df_elections,
                x='Election',
                y='Count',
                title="Voter Participation in Elections",
                labels={'Election': 'Election', 'Count': 'Number of Voters'},
                text_auto=True,  
                color='Election'
            )

            # adding the histogram to the context
            context['election_histogram'] = mark_safe(fig_hist.to_html(full_html=False))
        else:
            context['election_histogram'] = "<p>No data available.</p>"

        return context
