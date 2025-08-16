from django.urls import path, include
from .views import generate_pdf
urlpatterns = [

    path('demo/', generate_pdf, name='report_gen'),

]
