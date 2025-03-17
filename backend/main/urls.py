"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from . import views
from . import views_with_api

urlpatterns = [
    path('', RedirectView.as_view(url='/static/index.html')),
    path("api/get_csrf_token/", views.get_csrf_token, name="get_csrf_token"),
    path("api/run_information/", views_with_api.run_information_list, name="run_information"),
    path("api/step_name_list/", views_with_api.step_name_list, name="step_name_list"),
    path("api/workflow_name_list/", views_with_api.workflow_name_list, name="workflow_name_list"),
    
    path("api/toggle_favourite/", views_with_api.toggle_favourite, name="toggle_favourite"),
    path("api/add_tag/", views_with_api.add_tag, name="add_tag"),
    path("api/delete_tag/", views_with_api.delete_tag, name="delete_tag"),
    path("api/add_run/", views_with_api.add_run, name="add_run"),
    path("api/delete_run/", views_with_api.delete_run, name="delete_run"),
    path("api/continue_run/", views_with_api.continue_run, name="continue_run"),
    path("api/add_plot/", views_with_api.add_plot, name="add_plot"),
    path("api/add_step/", views_with_api.add_step, name="add_step"),
    path("api/delete_step/", views_with_api.delete_step, name="delete_step"),
    path("api/update_step/", views_with_api.update_step, name="update_step"),
    path("api/navigate_to_step/", views_with_api.navigate_to_step, name="navigate_to_step"),
    path("api/export_workflow/", views_with_api.export_workflow, name="export_workflow"),
    path("api/download_plots/", views_with_api.download_plots, name="download_plots"), #might function?
    path("api/download_table/", views_with_api.download_table, name="download_table"), #might function?
    path("api/get_step_parameters/", views_with_api.get_step_parameters, name="get_step_parameters"),
    path("api/get_step_plots/", views_with_api.get_step_plots, name="get_step_plots"),
    path("api/get_step_table/", views_with_api.get_step_table, name="get_step_table"),
    path("api/get_run_data/", views_with_api.get_run_data, name="get_run_data"),

    path("api/settings/", include("settings.urls")),

    #old routes, not yet implemented as api endpints, see notion card 
    path("databases", views.databases, name="databases"),
    path("databases/upload", views.database_upload, name="database_upload"),
    path("databases/delete", views.database_delete, name="database_delete"),
    path("admin/", admin.site.urls),
]