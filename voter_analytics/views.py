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
        # Prevent returning any voter records
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve all voter birth years
        birth_years = Voter.objects.values_list('dob', flat=True)
        birth_years = [dob.year for dob in birth_years if dob]  # Extract years

        if birth_years:
            # Convert to DataFrame
            df = pd.DataFrame(birth_years, columns=['year'])
            birth_year_counts = df['year'].value_counts().reset_index()
            birth_year_counts.columns = ['year', 'count']

            # Create bar chart with plotly.express
            fig = px.bar(birth_year_counts, x='year', y='count', title="Voter Distribution by Year of Birth")

            # Convert to HTML and pass to context
            context['birth_year_graph'] = mark_safe(fig.to_html(full_html=False))
        else:
            context['birth_year_graph'] = "<p>No data available.</p>"

        return context
   
