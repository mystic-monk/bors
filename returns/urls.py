from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('access/', views.access_login, name='access_login'),
    path('access/logout/', views.access_logout, name='access_logout'),
    path('tokens/', views.admin_tokens, name='admin_tokens'),
    path('tokens/<int:pk>/toggle/', views.toggle_access, name='toggle_access'),
    path('tokens/<int:pk>/regenerate/', views.regenerate_token, name='regenerate_token'),
    path('tokens/regenerate-all/', views.regenerate_all_tokens, name='regenerate_all_tokens'),
    path('return/new/', views.step_general, name='step_general_new'),
    path('return/<int:pk>/edit/general/', views.step_general, name='step_general'),
    path('return/<int:pk>/licences/', views.step_licence, name='step_licence'),
    path('return/<int:pk>/emissions/', views.step_emissions, name='step_emissions'),
    path('return/<int:pk>/accessibility/', views.step_accessibility, name='step_accessibility'),
    path('return/<int:pk>/declaration/', views.step_declaration, name='step_declaration'),
    path('return/<int:pk>/success/', views.success, name='success'),
    path('return/<int:pk>/export/', views.export_excel, name='export_excel'),
    path('staff/export/excel/', views.export_all_excel, name='export_all_excel'),
    path('staff/export/json/', views.export_all_json, name='export_all_json'),
    path('staff/seed-import/', views.admin_seed_import, name='admin_seed_import'),
    path('staff/seed-template/', views.download_seed_template, name='download_seed_template'),
    path('staff/locks/', views.admin_locks, name='admin_locks'),
    path('staff/locks/<int:year>/unlock/', views.unlock_year, name='unlock_year'),
]
