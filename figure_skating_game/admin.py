from django.contrib import admin
from .models import *


# Register your models here.

admin.site.register(Skater)
admin.site.register(Element)
admin.site.register(Program)
admin.site.register(ProgramElementOrder)
admin.site.register(Competition)
admin.site.register(ExecutedProgram)
admin.site.register(ExecutedElement)
admin.site.register(ElementProbability)
