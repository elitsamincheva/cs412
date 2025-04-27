from django import forms
from .models import Competition, Skater

class CompetitionForm(forms.ModelForm):
    skaters = forms.ModelMultipleChoiceField(
        queryset=Skater.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Competition
        fields = ['name', 'location', 'skaters']
