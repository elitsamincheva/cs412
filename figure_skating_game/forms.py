from django import forms
from .models import Competition, Skater, Program


class CompetitionForm(forms.ModelForm):
    skaters = forms.ModelMultipleChoiceField(
        queryset=Skater.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Competition
        fields = ['name', 'location', 'skaters']


# Define a form to select programs for skaters
class SelectProgramsForm(forms.Form):
    def __init__(self, skaters, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for skater in skaters:
            # Create a dropdown field for each skater to select their program
            programs = Program.objects.filter(skater=skater)
            self.fields[f'skater_{skater.id}'] = forms.ModelChoiceField(
                queryset=programs,
                label=f'Select Program for {skater.first_name} {skater.last_name}'
            )