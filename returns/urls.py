from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('return/new/', views.step_general, name='step_general_new'),
    path('return/<int:pk>/edit/general/', views.step_general, name='step_general'),
    path('return/<int:pk>/licences/', views.step_licence, name='step_licence'),
    path('return/<int:pk>/emissions/', views.step_emissions, name='step_emissions'),
    path('return/<int:pk>/accessibility/', views.step_accessibility, name='step_accessibility'),
    path('return/<int:pk>/success/', views.success, name='success'),
    path('return/<int:pk>/export/', views.export_excel, name='export_excel'),
]
