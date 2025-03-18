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
from django.urls import path
from django.views.generic import RedirectView

from . import views
from . import viewswithapi

# TODO R If you have views that handle API requests, you can import those here
# from myapp import views

urlpatterns = [
    path('', RedirectView.as_view(url='/static/index.html')),
    path("api/ping/", views.ping, name="ping"),
    path("api/jannesjsontest/", views.jannesjsontest, name="jannesjsontest"),
    path("api/do_something_with_element_from_frontend/", views.do_something_with_element_from_frontend, name="do_something_with_element_from_frontend"),
    path("api/run_information/", viewswithapi.run_information_list, name="run_information"),
    path("api/step_name_list/", viewswithapi.step_name_list, name="step_name_list"),
    path("api/workflow_name_list/", viewswithapi.workflow_name_list, name="workflow_name_list"),
    
    path("api/toggle_favourite/", viewswithapi.toggle_favourite, name="toggle_favourite"),
    path("api/add_tag/", viewswithapi.add_tag, name="add_tag"),
    path("api/delete_tag/", viewswithapi.delete_tag, name="delete_tag"),
    path("api/add_run/", viewswithapi.add_run, name="add_run"),
    path("api/delete_run/", viewswithapi.delete_run, name="delete_run"),
    path("api/continue_run/", viewswithapi.continue_run, name="continue_run"),
    path("api/add_plot/", viewswithapi.add_plot, name="add_plot"),
    path("api/add_step/", viewswithapi.add_step, name="add_step"),
    path("api/delete_step/", viewswithapi.delete_step, name="delete_step"),
    path("api/update_step/", viewswithapi.update_step, name="update_step"),
    path("api/navigate_to_step/", viewswithapi.navigate_to_step, name="navigate_to_step"),
    path("api/export_workflow/", viewswithapi.export_workflow, name="export_workflow"),
    path("api/download_plots/", viewswithapi.download_plots, name="download_plots"), #might function?
    path("api/download_table/", viewswithapi.download_table, name="download_table"), #might function?
    path("api/get_step_form/", viewswithapi.get_step_form, name="get_step_form"),
    path("api/get_step_plots/", viewswithapi.get_step_plots, name="get_step_plots"),
    path("api/get_step_table/", viewswithapi.get_step_table, name="get_step_table"),
    path("api/get_run_data/", viewswithapi.get_run_data, name="get_run_data"),

    # TODO R API routes (if using Django for API)
    # path('api/', include('myapp.api.urls')),  # Example for API routes


    path("databases", views.databases, name="databases"),
    path("databases/upload", views.database_upload, name="database_upload"),
    path("databases/delete", views.database_delete, name="database_delete"),
    path("admin/", admin.site.urls),
]