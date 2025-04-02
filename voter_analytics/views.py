from django.shortcuts import render
from django.views.generic import ListView
from .models import Voter
from django.db.models import Min, Max
from datetime import datetime

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
