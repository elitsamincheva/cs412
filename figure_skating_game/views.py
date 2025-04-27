import random

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView

from .forms import CompetitionForm
from .models import *


class ShowAllSkaters(ListView):
    model = Skater
    template_name = 'figure_skating_game/skaters_list.html' 
    context_object_name = 'skaters'  

class ShowAllCompetitions(ListView):
    model = Competition
    template_name = 'figure_skating_game/show_all_comps.html' 
    context_object_name = 'competitions'

class CreateCompetitionView(CreateView):
    model = Competition 
    form_class = CompetitionForm  
    template_name = 'figure_skating_game/create_competition.html'  

    def form_valid(self, form):
        # Save the competition model
        competition = form.save()

        # Loop through the selected skaters from the form
        for skater in form.cleaned_data['skaters']:
            # Find a preset program for the skater
            program = skater.programs.filter(preset=True).first()
            if not program:
                continue  # Skip if no preset program found

            total_score = 0  # Initialize score

            # Create an ExecutedProgram to track performance at this competition
            executed_program = ExecutedProgram.objects.create(
                program=program,
                competition=competition,
                total_score=0  # Will be updated after simulating elements
            )

            # Get ordered elements in the program
            elements = ProgramElementOrder.objects.filter(program=program).order_by('order')

            # Simulate execution of each element
            for order, peo in enumerate(elements, start=1):
                element = peo.element

                # Get success probability for this skater-element combo
                prob_obj = skater.element_probs.filter(element=element).first()
                success_rate = prob_obj.success_rate if prob_obj else 0.5

                # Simulate whether the element is executed successfully
                success = random.random() < success_rate

                # Generate a GOE depending on whether the element was successful
                goe = round(random.uniform(-3, 3), 2) if success else round(random.uniform(-5, 0), 2)

                # GOE contribution: 10% of base value per GOE point
                base_value = float(element.base_value)
                score = base_value + (goe * 0.1 * base_value)

                # Add to total score (but don’t allow negative contributions)
                total_score += max(score, 0)

                # Record the executed element
                ExecutedElement.objects.create(
                    executed_program=executed_program,
                    element=element,
                    order=order,
                    goe=goe
                )

            # Save the final total score for the executed program
            executed_program.total_score = round(total_score, 2)
            executed_program.save()

        # Redirect to the results page with the competition ID
        return redirect('competition_results', competition_id=competition.id)

class SkaterDetailView(DetailView):
    model = Skater
    template_name = 'figure_skating_game/skater_detail.html'
    context_object_name = 'skater'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skater = self.object

        # Get programs and executed programs
        context['programs'] = Program.objects.filter(skater=skater)
        context['executed_programs'] = ExecutedProgram.objects.filter(program__skater=skater)

        # Get success probabilities
        context['element_probs'] = skater.element_probs.select_related('element')

        return context
