# models.py
# defines the core data models for the figure skating app,
# including skaters, elements, programs, competitions, and executed results

from django.db import models
from django.utils.timezone import now

class Skater(models.Model):
    """represents an individual figure skater"""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nationality = models.CharField(max_length=100)
    birth_date = models.DateField()
    hometown = models.CharField(max_length=100, blank=True, null=True)
    skating_club = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='skater_images/')

    def __str__(self):
        """return full name for display"""
        return f"{self.first_name} {self.last_name}"

class Element(models.Model):
    """represents an individual skating element (jump, spin, etc.)"""
    ELEMENT_TYPES = [
        ('JUMP', 'Jump'),
        ('SPIN', 'Spin'),
        ('STEP', 'Step Sequence'),
        ('CHOREO', 'Choreographic'),
    ]

    name = models.CharField(max_length=50)  # e.g., "Triple Axel"
    code = models.CharField(max_length=10, unique=True) # e.g., "3A"
    element_type = models.CharField(max_length=10, choices=ELEMENT_TYPES)
    base_value = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        """return code and name for display"""
        return f"{self.code} - {self.name}"

class ElementProbability(models.Model):
    """stores the probability a skater successfully performs a specific element"""
    skater = models.ForeignKey(Skater, on_delete=models.CASCADE, related_name='element_probs')
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    success_rate = models.FloatField()  # Value between 0 and 1

    class Meta:
        unique_together = ('skater', 'element') # one entry per skater-element pair

    def __str__(self):
        """return readable probability description"""
        return f"{self.skater.first_name} {self.skater.last_name} - {self.element.name}: {self.success_rate:.0%}"

class Program(models.Model):
    """a set of elements choreographed for a skater"""
    title = models.CharField(max_length=100)
    skater = models.ForeignKey(Skater, on_delete=models.CASCADE, related_name='programs')
    elements = models.ManyToManyField(Element, through='ProgramElementOrder')   # element order defined in through table
    preset = models.BooleanField(default=False) # default program for a skater is their current season free skate (or most recent free skate)

    def __str__(self):
        """return program title and skater"""
        return f"{self.title} ({self.skater.first_name} {self.skater.last_name})"

class ProgramElementOrder(models.Model):
    """intermediate model for ordering elements in a program"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('program', 'order')  # no duplicate order in a program
        ordering = ['order']

    def __str__(self):
        """return the element order and name"""
        return f"{self.order} {self.element}"

class Competition(models.Model):
    """represents a competition event"""
    name = models.CharField(max_length=100)
    date = models.DateField(default=now)
    location = models.CharField(max_length=100)
    skaters = models.ManyToManyField(Skater, related_name='competitions')

    def __str__(self):
        """return competition name and date"""
        return f"{self.name} ({self.date})"

class ExecutedProgram(models.Model):
    """a specific program executed at a competition with a score"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='executions')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='executed_programs')
    total_score = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ['-total_score'] # highest scores first

    def __str__(self):
        """return execution summary"""
        return f"{self.program} at {self.competition} - {self.total_score}"

class ExecutedElement(models.Model):
    """tracks individual element performance within an executed program"""
    executed_program = models.ForeignKey(ExecutedProgram, on_delete=models.CASCADE, related_name='executed_elements')
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    goe = models.DecimalField(max_digits=4, decimal_places=2)   # grade of execution

    class Meta:
        ordering = ['order']    # preserve element order in program