import random

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import CreateView
from django.db.models import Max, Case, When, Prefetch

from .forms import CompetitionForm, SelectProgramsForm, ProgramForm
from .models import *


class ShowAllSkaters(ListView):
    model = Skater
    template_name = 'figure_skating_game/skaters_list.html' 
    context_object_name = 'skaters'  
    paginate_by = 9

class ShowAllCompetitions(ListView):
    model = Competition
    template_name = 'figure_skating_game/show_all_comps.html' 
    context_object_name = 'competitions'
    paginate_by = 9

class CreateCompetitionView(CreateView):
    model = Competition
    form_class = CompetitionForm
    template_name = 'figure_skating_game/create_competition.html'

    def form_valid(self, form):
        competition = form.save()
        skater_ids = ','.join(str(skater.id) for skater in form.cleaned_data['skaters'])
        redirect_url = reverse('select_programs') + f'?competition_id={competition.id}&skaters={skater_ids}'
        print(f"Redirecting to: {redirect_url}")  # Debugging
        print(f"Competition ID: {competition.id}")  # Debugging
        print(f"Skater IDs: {skater_ids}")  # Debugging
        return redirect(redirect_url)
    
class SelectProgramsView(FormView):  # Changed to FormView
    template_name = 'figure_skating_game/select_programs.html'
    form_class = SelectProgramsForm
    success_url = None  # Will be set dynamically

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get the skater IDs from the query string
        skater_ids_str = self.request.GET.get('skaters')
        if skater_ids_str:
            skater_ids = [int(id) for id in skater_ids_str.split(',')]
            kwargs['skaters'] = Skater.objects.filter(id__in=skater_ids)
        else:
            kwargs['skaters'] = Skater.objects.none()  # Or handle the error as appropriate
        return kwargs

    def form_valid(self, form):
        competition_id = self.request.GET.get('competition_id')
        competition = Competition.objects.get(id=competition_id)
        self.success_url = reverse('competition_detail', kwargs={'pk': competition.pk})

        for field_name, program in form.cleaned_data.items():
            if field_name.startswith('skater_'):
                #  loop through the selected skaters from the form
                skater_id = int(field_name.split('_')[1])  # Extract skater ID from field name
                skater = Skater.objects.get(pk=skater_id)  # Get the skater object

                total_score = 0  # initialize score

                # create an ExecutedProgram to track performance at this competition
                executed_program = ExecutedProgram.objects.create(
                    program=program,
                    competition=competition,
                    total_score=0  # will be updated after simulating elements
                )

                # get ordered elements in the program
                elements = ProgramElementOrder.objects.filter(program=program).order_by('order')

                # simulate execution of each element
                for order, peo in enumerate(elements, start=1):
                    element = peo.element

                    # get success probability for this skater-element combo
                    prob_obj = skater.element_probs.filter(element=element).first()
                    success_rate = prob_obj.success_rate if prob_obj else 0.5

                    # simulate whether the element is executed successfully
                    success = random.random() < success_rate

                    # generate a GOE depending on whether the element was successful
                    goe = round(random.uniform(-3, 3), 2) if success else round(random.uniform(-5, 0), 2)

                    # GOE contribution: 10% of base value per GOE point
                    base_value = float(element.base_value)
                    score = base_value + (goe * 0.1 * base_value)

                    # add to total score (but don’t allow negative contributions)
                    total_score += max(score, 0)

                    # record the executed element
                    ExecutedElement.objects.create(
                        executed_program=executed_program,
                        element=element,
                        order=order,
                        goe=goe
                    )

                # save the final total score for the executed program
                executed_program.total_score = round(total_score, 2)
                executed_program.save()

        return super().form_valid(form)  # Redirect using success_url

    def get_success_url(self):
        return self.success_url

class SkaterDetailView(DetailView):
    model = Skater
    template_name = 'figure_skating_game/skater_detail.html'
    context_object_name = 'skater'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skater = self.object

        # get programs and executed programs
        programs = Program.objects.filter(skater=skater)
        executed_programs = ExecutedProgram.objects.filter(program__skater=skater)

        # paginate programs if more than 6
        if programs.count() > 6:
            program_paginator = Paginator(programs, 6)
            page_program = self.request.GET.get('page_program')
            try:
                context['programs'] = program_paginator.get_page(page_program)
            except PageNotAnInteger:
                context['programs'] = program_paginator.get_page(1)
            except EmptyPage:
                context['programs'] = program_paginator.get_page(program_paginator.num_pages)
        else:
            context['programs'] = programs

        # paginate executed programs if more than 6
        if executed_programs.count() > 6:
            competition_paginator = Paginator(executed_programs, 6)
            page_competition = self.request.GET.get('page_competition')
            try:
                context['executed_programs'] = competition_paginator.get_page(page_competition)
            except PageNotAnInteger:
                context['executed_programs'] = competition_paginator.get_page(1)
            except EmptyPage:
                context['executed_programs'] = competition_paginator.get_page(competition_paginator.num_pages)
        else:
            context['executed_programs'] = executed_programs
        return context


class HomeView(ListView):
    model = Skater
    template_name = 'figure_skating_game/home.html'
    context_object_name = 'skaters'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the 3 most recent competitions
        context['competitions'] = Competition.objects.all().order_by('-date')[:3]

        # get the top 10 skaters with the highest ever scores (no repeats)
        # assuming ExecutedProgram is the model where skater scores are stored
        highest_scores = ExecutedProgram.objects.values('program__skater').annotate(
            max_score=Max('total_score')
        ).order_by('-max_score')[:10]

        # get skaters corresponding to the top 10 highest scores
        skater_ids = [entry['program__skater'] for entry in highest_scores]
        preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(skater_ids)])
        context['skaters'] = Skater.objects.filter(id__in=skater_ids).order_by(preserved_order)

        return context
    

class ShowAllPrograms(ListView):
    model = Program
    template_name = 'figure_skating_game/show_all_programs.html'
    context_object_name = 'programs'
    paginate_by = 9

    def get_queryset(self):
        return Program.objects.annotate(top_score=Max('executions__total_score'))
    


class CompetitionDetailView(DetailView):
    model = Competition
    template_name = 'figure_skating_game/competition_detail.html'
    context_object_name = 'competition'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        competition = self.object
        executed_programs = ExecutedProgram.objects.filter(competition=competition).order_by('-total_score')
        context['executed_programs'] = executed_programs
        return context
    
class ProgramDetailView(DetailView):
    model = Program
    template_name = 'figure_skating_game/program_detail.html'
    context_object_name = 'program'

    def get_queryset(self):
        """
        Prefetch related data for efficiency.
        """
        return Program.objects.prefetch_related(
            'skater',  # prefetch the skater
            Prefetch(
                'executions',
                queryset=ExecutedProgram.objects.select_related('competition').order_by('-competition__date')
            ), # prefetch executed programs, select competition, and order
            'elements' # prefetch the elements
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program = self.get_object()

        context['executed_programs'] = program.executions.all() # access the prefetched executions

        return context
    
class CreateProgramView(CreateView):
    model = Program
    form_class = ProgramForm
    template_name = 'figure_skating_game/create_program.html'

    def form_valid(self, form):
        program = form.save()

        elements_data = [form.cleaned_data.get(f'element_{i}') for i in range(1, 13)]
        elements_data = [e for e in elements_data if e is not None]

        order = 1
        for element in elements_data:
            ProgramElementOrder.objects.create(
                program=program,
                element=element,
                order=order
            )
            order += 1

        return redirect(reverse('program_detail', kwargs={'pk': program.pk}))  # Replace 'program_detail' with your actual detail view name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skaters'] = Skater.objects.all()
        context['element_fields'] = []
        form = self.form_class()  # Instantiate the form
        for i in range(1, 13):
            context['element_fields'].append(form[f'element_{i}'])  # Access the field directly
        context['form'] = form
        return context