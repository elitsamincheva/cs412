# this file defines all forms used in the figure skating app
# it includes:
# - competitionform: for creating or editing competitions and selecting participating skaters
# - selectprogramsform: for assigning programs to skaters dynamically based on who is competing
# - programform: for building a valid program with 12 unique elements that meet isu composition rules
# - skaterform: for creating or editing a skater's profile including name, nationality, and image

from django import forms
from .models import Competition, Skater, Program, Element

class CompetitionForm(forms.ModelForm):
    """
    form for creating or updating a competition
    allows selecting multiple skaters who will participate in the competition
    """
    skaters = forms.ModelMultipleChoiceField(
        queryset=Skater.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Competition
        fields = ['name', 'location', 'skaters']

class SelectProgramsForm(forms.Form):
    """
    form for selecting programs for each skater
    dynamic fields are created based on the skaters passed to the form
    """
    def __init__(self, skaters, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for skater in skaters:
            # create a dropdown field for each skater to select their program
            programs = Program.objects.filter(skater=skater)
            self.fields[f'skater_{skater.id}'] = forms.ModelChoiceField(
                queryset=programs,
                label=f'Select Program for {skater.first_name} {skater.last_name}'
            )

class ProgramForm(forms.ModelForm):
    """
    Form for creating a Program with specific element slots
    Per the ISU requirements:
        1 ChSq
        1 StSq
        3 Spins
        7 Jumps
        No repeats
    """
    class Meta:
        model = Program
        fields = ['title', 'skater']

    # element selection fields for the program
    element_1 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 1")
    element_2 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 2")
    element_3 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 3")
    element_4 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 4")
    element_5 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 5")
    element_6 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 6")
    element_7 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 7")
    element_8 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 8")
    element_9 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 9")
    element_10 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 10")
    element_11 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 11")
    element_12 = forms.ModelChoiceField(queryset=Element.objects.all(), required=True, empty_label="Select Element 12")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # customize field labels to be 1 through 12
        for i in range(1, 13):
            self.fields[f'element_{i}'].label = f'Element {i}'

    def clean(self):
        """
        custom validation for the program form
        checks that the program contains 7 unique jumps, 3 spins, 1 step sequence, and 1 choreo sequence
        """
        cleaned_data = super().clean()
        elements = [cleaned_data.get(f'element_{i}') for i in range(1, 13)]
        elements = [e for e in elements if e is not None]

        # check if any element is repeated
        if len(elements) != len(set(elements)):
            raise forms.ValidationError("Each element must be unique.")

        # count the number of each element type
        jump_count = sum(1 for e in elements if e and e.element_type == 'JUMP')
        spin_count = sum(1 for e in elements if e and e.element_type == 'SPIN')
        step_count = sum(1 for e in elements if e and e.element_type == 'STEP')
        choreo_count = sum(1 for e in elements if e and e.element_type == 'CHOREO')

        # validate that the correct number of each element type is present
        if jump_count != 7:
            raise forms.ValidationError("There must be exactly 7 jumps.")
        if spin_count != 3:
            raise forms.ValidationError("There must be exactly 3 spins.")
        if step_count != 1:
            raise forms.ValidationError("There must be exactly 1 step sequence.")
        if choreo_count != 1:
            raise forms.ValidationError("There must be exactly 1 choreo sequence.")

        return cleaned_data
    
class SkaterForm(forms.ModelForm):
    """
    form for creating or updating a skater's profile
    includes fields for the skater's name, nationality, date of birth, skating club, hometown, and image
    """
    class Meta:
        model = Skater
        fields = ['first_name', 'last_name', 'nationality', 'birth_date', 'skating_club', 'hometown', 'image']