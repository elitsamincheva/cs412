import random

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, FormView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.db.models import Max, Case, When, Prefetch, Count, Avg, Q


from django.http import JsonResponse  
from django.http import HttpResponseRedirect

from .forms import CompetitionForm, SelectProgramsForm, ProgramForm, SkaterForm
from .models import *

class ShowAllSkaters(ListView):
    """
    view to display a paginated list of all skaters
    """
    model = Skater
    template_name = 'figure_skating_game/skaters_list.html' 
    context_object_name = 'skaters'  
    paginate_by = 9  # show 9 skaters per page


class ShowAllCompetitions(ListView):
    """
    view to display a paginated list of all competitions
    """
    model = Competition
    template_name = 'figure_skating_game/show_all_comps.html' 
    context_object_name = 'competitions'
    paginate_by = 9  # show 9 competitions per page


class CreateCompetitionView(CreateView):
    """
    view to create a new competition and redirect to program selection
    """
    model = Competition
    form_class = CompetitionForm
    template_name = 'figure_skating_game/create_competition.html'

    def form_valid(self, form):
        """
        called when form is valid. saves the competition and
        redirects to program selection view with skater ids
        """
        competition = form.save()

        # collect the skater ids and pass them in the query string
        skater_ids = ','.join(str(skater.id) for skater in form.cleaned_data['skaters'])

        # build the redirect url to select programs for this competition
        redirect_url = reverse('select_programs') + f'?competition_id={competition.id}&skaters={skater_ids}'
        return redirect(redirect_url)
    
class SelectProgramsView(FormView):
    """
    view for selecting programs for skaters to compete in a given competition
    handles form input and simulates program execution including GOE and scoring
    """
    template_name = 'figure_skating_game/select_programs.html'
    form_class = SelectProgramsForm
    success_url = None  # will be set dynamically after form submission

    def get_form_kwargs(self):
        """
        override to pass selected skaters into the form
        gets skater ids from the query string and filters queryset
        """
        kwargs = super().get_form_kwargs()
        skater_ids_str = self.request.GET.get('skaters')
        if skater_ids_str:
            # convert query string of ids into a list of integers
            skater_ids = [int(id) for id in skater_ids_str.split(',')]
            kwargs['skaters'] = Skater.objects.filter(id__in=skater_ids)
        else:
            # no skaters passed — provide an empty queryset
            kwargs['skaters'] = Skater.objects.none()
        return kwargs

    def form_valid(self, form):
        """
        called when the form is valid
        simulates the execution of selected programs in a competition
        """
        competition_id = self.request.GET.get('competition_id')
        competition = Competition.objects.get(id=competition_id)
        self.success_url = reverse('competition_detail', kwargs={'pk': competition.pk})

        # loop through all fields in the form
        for field_name, program in form.cleaned_data.items():
            if field_name.startswith('skater_'):
                # extract skater id from field name like 'skater_5'
                skater_id = int(field_name.split('_')[1])
                skater = Skater.objects.get(pk=skater_id)

                total_score = 0  # initialize score for this skater’s program

                # create a record of the program being executed at this competition
                executed_program = ExecutedProgram.objects.create(
                    program=program,
                    competition=competition,
                    total_score=0  # will be updated after simulating elements
                )

                # get elements in order for this program
                elements = ProgramElementOrder.objects.filter(program=program).order_by('order')

                # simulate execution of each element in the program
                for order, peo in enumerate(elements, start=1):
                    element = peo.element

                    # get the success rate for this skater and element
                    prob_obj = skater.element_probs.filter(element=element).first()
                    success_rate = prob_obj.success_rate if prob_obj else 0.5

                    # determine if the element was successfully executed
                    success = random.random() < success_rate

                    # assign a grade of execution (goe)
                    goe = round(random.uniform(-3, 3), 2) if success else round(random.uniform(-5, 0), 2)

                    # calculate the score for this element
                    base_value = float(element.base_value)
                    score = base_value + (goe * 0.1 * base_value)

                    # add score to total, making sure it’s not negative
                    total_score += max(score, 0)

                    # save the result of this element execution
                    ExecutedElement.objects.create(
                        executed_program=executed_program,
                        element=element,
                        order=order,
                        goe=goe
                    )

                # save the final total score after all elements are processed
                executed_program.total_score = round(total_score, 2)
                executed_program.save()

        return super().form_valid(form)

    def get_success_url(self):
        """
        return the url to redirect to after a successful form submission
        """
        return self.success_url

class SkaterDetailView(DetailView):
    """
    view for showing a single skater’s detail page
    displays their programs and performances in competitions
    """
    model = Skater
    template_name = 'figure_skating_game/skater_detail.html'
    context_object_name = 'skater'

    def get_context_data(self, **kwargs):
        """
        adds the skater’s programs and executed programs to the context,
        with pagination if there are more than 6 of either
        """
        context = super().get_context_data(**kwargs)
        skater = self.object

        # get all programs made by this skater
        programs = Program.objects.filter(skater=skater)

        # get all performances this skater has done in competitions
        executed_programs = ExecutedProgram.objects.filter(program__skater=skater)

        # if there are more than 6 programs, paginate them
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
            # if 6 or fewer, just show them all
            context['programs'] = programs

        # if more than 6 executed programs, paginate those too
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
            # show all if 6 or fewer
            context['executed_programs'] = executed_programs

        # creates the URL for the "Create Program" button, passing the skater's PK
        context['create_program_url'] = reverse(
            'create_program_for_skater', kwargs={'pk': skater.pk}
        )  
        
        return context

class HomeView(ListView):
    """
    view for the home page
    shows recent competitions and the top 10 skaters by best score ever
    """
    model = Skater
    template_name = 'figure_skating_game/home.html'
    context_object_name = 'skaters'

    def get_context_data(self, **kwargs):
        """
        adds recent competitions and top skaters to context
        """
        context = super().get_context_data(**kwargs)

        # get the 3 most recent competitions
        context['competitions'] = Competition.objects.all().order_by('-date')[:3]

        # get the top 10 skaters by their highest total score from any program
        highest_scores = ExecutedProgram.objects.values('program__skater').annotate(
            max_score=Max('total_score')  # get best score per skater
        ).order_by('-max_score')[:10]

        # get the skater ids in the right order
        skater_ids = [entry['program__skater'] for entry in highest_scores]

        # preserve that order when fetching the skater objects
        preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(skater_ids)])
        context['skaters'] = Skater.objects.filter(id__in=skater_ids).order_by(preserved_order)

        return context
    
class ShowAllPrograms(ListView):
    """
    view for listing all programs
    shows them in pages of 9 and adds their highest score if they've been used
    """
    model = Program
    template_name = 'figure_skating_game/show_all_programs.html'
    context_object_name = 'programs'
    paginate_by = 9  # show 9 programs per page

    def get_queryset(self):
        """
        annotate each program with its highest score from any execution
        """
        return Program.objects.annotate(
            top_score=Max('executions__total_score')  # add 'top_score' field to each program
        )
    
class CompetitionDetailView(DetailView):
    """
    view for showing the details of a specific competition
    includes list of programs that were performed in it, sorted by score (i.e. the results of the comp)
    """
    model = Competition
    template_name = 'figure_skating_game/competition_detail.html'
    context_object_name = 'competition'

    def get_context_data(self, **kwargs):
        """
        adds extra info to the template like the executed programs,
        sorted by total score (highest first)
        """
        context = super().get_context_data(**kwargs)
        competition = self.object  # the current competition being viewed

        # get all executed programs in this competition, sorted by score
        executed_programs = ExecutedProgram.objects.filter(
            competition=competition
        ).order_by('-total_score')

        context['executed_programs'] = executed_programs
        return context

class ProgramDetailView(DetailView):
    """
    view for showing the details of a specific program
    includes program info, executed runs, and total base value of elements
    """
    model = Program
    template_name = 'figure_skating_game/program_detail.html'
    context_object_name = 'program'

    def get_queryset(self):
        """
        gets the program queryset and prefetches related data
        so it's faster and doesn't hit the database a lot
        """
        return Program.objects.prefetch_related(
            'skater',  # get the skater info with the program
            Prefetch(
                'executions',
                queryset=ExecutedProgram.objects.select_related('competition').order_by('-competition__date')
            ),  # get the program's past executions with competition info, sorted by most recent
            'elements'  # get all elements in the program
        )

    def get_context_data(self, **kwargs):
        """
        adds extra info to the template, like executed runs and base value.
        """
        context = super().get_context_data(**kwargs)
        program = self.get_object()  # get the program being viewed

        context['executed_programs'] = program.executions.all()  # list of all runs of the program

        # calculate the total base value of the elements in the program
        total_base_value = sum(element.base_value for element in program.elements.all())
        context['total_base_value'] = total_base_value

        return context
    
class CreateProgramView(CreateView):
    model = Program
    form_class = ProgramForm
    template_name = 'figure_skating_game/create_program.html'

    def get_initial(self):
        initial = super().get_initial()
        skater_pk = self.kwargs.get('pk')  # Get skater pk from URL
        if skater_pk:
            skater = get_object_or_404(Skater, pk=skater_pk)
            initial['skater'] = skater  # Set initial value for skater field
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(initial=self.get_initial()) # Pass initial data to form
        context['elements'] = Element.objects.all()
        context['slots'] = range(1, 13)
        context['skater_pk'] = self.kwargs.get('pk') #Pass the skater pk to the template
        return context

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
        return redirect(reverse('program_detail', kwargs={'pk': program.pk})) # Changed this

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context) #added this
    

class UpdateSkaterView(UpdateView):
    model = Skater
    form_class = SkaterForm  # Use a form to handle updates
    template_name = 'figure_skating_game/update_skater.html'
    pk_url_kwarg = 'pk'

    def get_success_url(self):
        return reverse('skater_detail', kwargs={'pk': self.object.pk})
    

class CompetitionDeleteView(DeleteView):
    """
    view for handling deletion of a competition object
    shows the detail template but adds delete/cancel handling via post
    """
    model = Competition
    template_name = 'figure_skating_game/competition_detail.html' 
    success_url = reverse_lazy('show_all_comps')  # after successful deletion go to see all competitions

    def post(self, request, *args, **kwargs):
        """
        handles post request to either delete the competition or cancel the action
        """
        if "delete" in request.POST:  # check if the delete button was pressed
            self.object = self.get_object()  # get the competition instance
            self.object.delete()  # delete the competition
            return redirect(self.success_url)  # redirect to competition list
        elif "cancel" in request.POST:
            return redirect(reverse('competition_detail', kwargs={'pk': self.kwargs['pk']}))  # go back to detail view
        else:
            return super().post(request, *args, **kwargs)  # fallback to default behavior

    def get_context_data(self, **kwargs):
        """
        adds the competition object to the context for template access
        """
        context = super().get_context_data(**kwargs)
        context['competition'] = self.get_object()  # makes competition available in the template
        return context


class ElementListView(ListView):
    model = Element
    template_name = 'figure_skating_game/element_list.html'
    context_object_name = 'elements'

class ElementUsageView(ListView):
    model = Competition
    template_name = 'figure_skating_game/element_usage_report.html'
    context_object_name = 'competitions'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if not pk:
            return Competition.objects.none()

        try:
            element = Element.objects.get(pk=pk)
        except Element.DoesNotExist:
            return Competition.objects.none()

        competitions = Competition.objects.filter(
            executed_programs__executed_elements__element=element
        ).prefetch_related(
            'executed_programs',
            'executed_programs__program__skater',
            'executed_programs__executed_elements',
            'executed_programs__executed_elements__element' # Access the element
        ).annotate(
            element_count=Count('executed_programs__executed_elements', filter=Q(executed_programs__executed_elements__element=element)),
            avg_goe=Avg('executed_programs__executed_elements__goe', filter=Q(executed_programs__executed_elements__element=element))
        ).distinct()
        return competitions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        if pk:
            try:
                element = Element.objects.get(pk=pk)
                context['element'] = element
                context['element_name'] = element.name
            except Element.DoesNotExist:
                context['element_error'] = "Element not found"
        return context