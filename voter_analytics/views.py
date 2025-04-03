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
    model = Voter
    template_name = "voters/voter_list.html"
    context_object_name = "voters"
    paginate_by = 100  # Show 100 records per page

    def get_queryset(self):
        """Filter the voters based on query parameters."""
        queryset = Voter.objects.all()

        # Party affiliation filter
        party_filter = self.request.GET.get("party")
        if party_filter:
            queryset = queryset.filter(party=party_filter)

        # Minimum date of birth filter
        min_dob_filter = self.request.GET.get("min_dob")
        if min_dob_filter:
            try:
                min_dob_date = datetime.strptime(min_dob_filter, '%Y').date()
                queryset = queryset.filter(dob__gte=min_dob_date)
            except ValueError:
                pass  # Invalid date format, ignore filter

        # Maximum date of birth filter
        max_dob_filter = self.request.GET.get("max_dob")
        if max_dob_filter:
            try:
                # Assume max_dob is a year and set it to the last day of the year (12-31)
                max_dob_date = datetime.strptime(max_dob_filter, '%Y').date().replace(month=12, day=31)
                queryset = queryset.filter(dob__lte=max_dob_date)
            except ValueError:
                pass  # Invalid date format, ignore filter
        # Voter score filter
        voter_score_filter = self.request.GET.get("voter_score")
        if voter_score_filter:
            queryset = queryset.filter(voter_score=voter_score_filter)

        # Election participation filter (check multiple elections)
        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        for election in elections:
            if self.request.GET.get(election):
                queryset = queryset.filter(**{election: True})

        return queryset

    def get_context_data(self, **kwargs):
        """Add extra context for filtering options."""
        context = super().get_context_data(**kwargs)

        # Get the available party affiliations
        parties = Voter.objects.values_list('party', flat=True).distinct()

        # Get the minimum and maximum birth years from the dataset
        min_birth_year = Voter.objects.aggregate(Min('dob'))['dob__min'].year
        max_birth_year = Voter.objects.aggregate(Max('dob'))['dob__max'].year

        years = list(range(min_birth_year, max_birth_year + 1))

        # Add these to the context
        context['parties'] = parties
        context['min_birth_year'] = min_birth_year
        context['max_birth_year'] = max_birth_year
        context['years'] = years
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']

        return context
    

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'  # Template for the detail view
    context_object_name = 'voter'  # Context variable name to use in the template


class GraphsView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'

    def get_queryset(self):
        # Start with all voters
        queryset = Voter.objects.all()

        # Party affiliation filter
        party_filter = self.request.GET.get("party")
        if party_filter:
            queryset = queryset.filter(party=party_filter)

        # Minimum date of birth filter
        min_dob_filter = self.request.GET.get("min_dob")
        if min_dob_filter:
            try:
                min_dob_date = datetime.strptime(min_dob_filter, '%Y').date()
                queryset = queryset.filter(dob__gte=min_dob_date)
            except ValueError:
                pass  # Invalid date format, ignore filter

        # Maximum date of birth filter
        max_dob_filter = self.request.GET.get("max_dob")
        if max_dob_filter:
            try:
                max_dob_date = datetime.strptime(max_dob_filter, '%Y').date().replace(month=12, day=31)
                queryset = queryset.filter(dob__lte=max_dob_date)
            except ValueError:
                pass  # Invalid date format, ignore filter

        # Voter score filter
        voter_score_filter = self.request.GET.get("voter_score")
        if voter_score_filter:
            queryset = queryset.filter(voter_score=voter_score_filter)

        # Election participation filter
        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        for election in elections:
            if self.request.GET.get(election):
                queryset = queryset.filter(**{election: True})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the available party affiliations
        parties = Voter.objects.values_list('party', flat=True).distinct()

        # Get the minimum and maximum birth years from the dataset
        min_birth_year = Voter.objects.aggregate(Min('dob'))['dob__min'].year
        max_birth_year = Voter.objects.aggregate(Max('dob'))['dob__max'].year

        years = list(range(min_birth_year, max_birth_year + 1))

        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']

        context['parties'] = parties
        context['min_birth_year'] = min_birth_year
        context['max_birth_year'] = max_birth_year
        context['years'] = years
        context['elections'] = elections

        # --- Voter Distribution by Year of Birth (Bar Chart) ---
        birth_years = self.get_queryset().values_list('dob', flat=True)
        birth_years = [dob.year for dob in birth_years if dob]  # Extract years

        if birth_years:
            df_years = pd.DataFrame({'year': birth_years})
            birth_year_counts = df_years['year'].value_counts().reset_index()
            birth_year_counts.columns = ['year', 'count']
            birth_year_counts = birth_year_counts.sort_values(by='year')  # Sort by year

            fig_bar = px.bar(
                birth_year_counts,
                x='year', 
                y='count', 
                title="Voter Distribution by Year of Birth",
                labels={'year': 'Year of Birth', 'count': 'Count'}
            )

            context['birth_year_graph'] = mark_safe(fig_bar.to_html(full_html=False))
        else:
            context['birth_year_graph'] = "<p>No data available.</p>"

        # --- Voter Distribution by Party Affiliation (Larger Pie Chart) ---
        parties = self.get_queryset().values_list('party', flat=True)
        parties = [p for p in parties if p]  # Remove None values

        if parties:
            df_parties = pd.DataFrame({'party': parties})
            party_counts = df_parties['party'].value_counts().reset_index()
            party_counts.columns = ['party', 'count']

            fig_pie = px.pie(
                party_counts,
                names='party', 
                values='count', 
                title="Voter Distribution by Party Affiliation",
                width=900,  # Increased width
                height=700   # Increased height
            )

            context['party_pie_chart'] = mark_safe(fig_pie.to_html(full_html=False))
        else:
            context['party_pie_chart'] = "<p>No data available.</p>"

        # --- Voter Participation in Elections (Histogram) ---
        election_counts = {election: self.get_queryset().filter(**{election: True}).count() for election in elections}

        if any(election_counts.values()):  # Check if there's data
            df_elections = pd.DataFrame(list(election_counts.items()), columns=['Election', 'Count'])

            fig_hist = px.bar(
                df_elections,
                x='Election',
                y='Count',
                title="Voter Participation in Elections",
                labels={'Election': 'Election', 'Count': 'Number of Voters'},
                text_auto=True,  # Show values on bars
                color='Election'
            )

            context['election_histogram'] = mark_safe(fig_hist.to_html(full_html=False))
        else:
            context['election_histogram'] = "<p>No data available.</p>"

        return context
