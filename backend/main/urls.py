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
from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views, views_settings
from . import views_with_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/get_csrf_token/", views.get_csrf_token, name="get_csrf_token"),
    path("api/run_information/", views_with_api.run_information_list, name="run_information"),
    path("api/step_list/", views_with_api.all_steps, name="step_list"),
    path("api/workflow_name_list/", views_with_api.workflow_name_list, name="workflow_name_list"),

    path("api/toggle_favourite/", views_with_api.toggle_favourite, name="toggle_favourite"),
    path("api/add_tag/", views_with_api.add_tag, name="add_tag"),
    path("api/delete_tag/", views_with_api.delete_tag, name="delete_tag"),
    path("api/add_run/", views_with_api.add_run, name="add_run"),
    path("api/delete_run/", views_with_api.delete_run, name="delete_run"),
    path("api/continue_run/", views_with_api.continue_run, name="continue_run"),
    path("api/update_run_name/", views_with_api.update_run_name, name="update_run_name"),
    path("api/add_plot/", views_with_api.add_plot, name="add_plot"),
    path("api/add_step/", views_with_api.add_step, name="add_step"),
    path("api/delete_step/", views_with_api.delete_step, name="delete_step"),
    path("api/update_step/", views_with_api.update_step, name="update_step"),
    path("api/navigate_to_step/", views_with_api.navigate_to_step, name="navigate_to_step"),
    path("api/save_workflow/", views_with_api.save_workflow, name="save_workflow"),
    path("api/download_table/", views_with_api.download_table, name="download_table"), #might function?
    path("api/get_step_form/", views_with_api.get_step_form, name="get_step_form"),
    path("api/get_step_plots/", views_with_api.get_step_plots, name="get_step_plots"),
    path("api/get_step_table/", views_with_api.get_step_table, name="get_step_table"),
    path("api/get_run_data/", views_with_api.get_run_data, name="get_run_data"),
    path("api/upload_file/", views_with_api.upload_file, name="upload_file"),
    path("api/calculate_step/", views_with_api.calculate_step, name="calculate_step"),

    path("api/load_settings", views_settings.load_settings, name="load_settings"),
    path("api/save_settings", views_settings.save_settings, name="save_settings"),
    path("api/download_plot", views_settings.download_plot, name="download_plot"),
    path("api/get_databases", views_settings.get_databases, name="get_databases"),
    path("api/upload_database", views_settings.database_upload, name="database_upload"),
    path("api/delete_database", views_settings.database_delete, name="database_delete"),

    # catches all urls unknown to the backend to check if the frontend at index.html knows them - must be last url
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]