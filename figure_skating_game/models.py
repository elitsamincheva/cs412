from django.db import models
from django.utils.timezone import now

class Skater(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nationality = models.CharField(max_length=100)
    birth_date = models.DateField()
    hometown = models.CharField(max_length=100, blank=True, null=True)
    skating_club = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='skater_images/')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Element(models.Model):
    ELEMENT_TYPES = [
        ('JUMP', 'Jump'),
        ('SPIN', 'Spin'),
        ('STEP', 'Step Sequence'),
        ('CHOREO', 'Choreographic'),
    ]

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    element_type = models.CharField(max_length=10, choices=ELEMENT_TYPES)
    base_value = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.code} - {self.name}"


class ElementProbability(models.Model):
    skater = models.ForeignKey(Skater, on_delete=models.CASCADE, related_name='element_probs')
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    success_rate = models.FloatField()  # Value between 0 and 1

    class Meta:
        unique_together = ('skater', 'element')

    def __str__(self):
        return f"{self.skater.first_name} {self.skater.last_name} - {self.element.name}: {self.success_rate:.0%}"



class Program(models.Model):
    title = models.CharField(max_length=100)
    skater = models.ForeignKey(Skater, on_delete=models.CASCADE, related_name='programs')
    elements = models.ManyToManyField(Element, through='ProgramElementOrder')  
    preset = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.skater.first_name} {self.skater.last_name})"


class ProgramElementOrder(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('program', 'order')
        ordering = ['order']
    def __str__(self):
        return f"{self.order} {self.element}"


class Competition(models.Model):
    name = models.CharField(max_length=100)
    # date = models.DateField(auto_now_add=True)
    date = models.DateField(default=now)
    location = models.CharField(max_length=100)
    skaters = models.ManyToManyField(Skater, related_name='competitions')

    def __str__(self):
        return f"{self.name} ({self.date})"



class ExecutedProgram(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='executions')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='executed_programs')
    total_score = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ['-total_score']

    def __str__(self):
        return f"{self.program} at {self.competition} - {self.total_score}"


class ExecutedElement(models.Model):
    executed_program = models.ForeignKey(ExecutedProgram, on_delete=models.CASCADE, related_name='executed_elements')
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    goe = models.DecimalField(max_digits=4, decimal_places=2) 

    class Meta:
        ordering = ['order']
