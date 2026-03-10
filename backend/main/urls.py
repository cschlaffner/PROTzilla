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

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/get_csrf_token/", views.get_csrf_token, name="get_csrf_token"),
    path("api/run_information/", views.run_information_list, name="run_information"),
    path("api/step_list/", views.all_steps, name="step_list"),
    path(
        "api/workflow_name_list/", views.workflow_name_list, name="workflow_name_list"
    ),
    path("api/toggle_favourite/", views.toggle_favourite, name="toggle_favourite"),
    path("api/add_tag/", views.add_tag, name="add_tag"),
    path("api/delete_tag/", views.delete_tag, name="delete_tag"),
    path("api/add_run/", views.add_run, name="add_run"),
    path("api/delete_run/", views.delete_run, name="delete_run"),
    path("api/continue_run/", views.continue_run, name="continue_run"),
    path("api/update_run_name/", views.update_run_name, name="update_run_name"),
    path("api/export_run/", views.export_run, name="export_run"),
    path("api/import_run/", views.import_run, name="import_run"),
    path("api/add_plot/", views.add_plot, name="add_plot"),
    path("api/add_step/", views.add_step, name="add_step"),
    path("api/delete_step/", views.delete_step, name="delete_step"),
    path("api/update_step/", views.update_step, name="update_step"),
    path("api/navigate_to_step/", views.navigate_to_step, name="navigate_to_step"),
    path("api/save_workflow/", views.save_workflow, name="save_workflow"),
    path(
        "api/download_table/", views.download_table, name="download_table"
    ),  # might function?
    path("api/get_step_form/", views.get_step_form, name="get_step_form"),
    path("api/get_step_plots/", views.get_step_plots, name="get_step_plots"),
    path(
        "api/get_step_visualizations/", 
        views.get_step_visualizations, 
        name="get_step_visualizations",
    ),
    path(
        "api/get_monomer_cif_for_visualization/", 
        views.get_monomer_cif_for_visualization, 
        name="get_monomer_cif_for_visualization",
    ),
    path(
        "api/get_current_step_output_labels/",
        views.get_current_step_output_labels,
        name="get_current_step_output_labels",
    ),
    path(
        "api/get_current_step_table_data/",
        views.get_current_step_table_data,
        name="get_current_step_table_data",
    ),
    path("api/get_run_data/", views.get_run_data, name="get_run_data"),
    path("api/upload_file/", views.upload_file, name="upload_file"),
    path("api/calculate_step/", views.calculate_step, name="calculate_step"),
    path("api/export_workflow/", views.export_workflow, name="export_workflow"),
    path("api/import_workflow/", views.import_workflow, name="import_workflow"),
    path("api/delete_workflow/", views.delete_workflow, name="delete_workflow"),
    path("api/load_settings", views_settings.load_plot_settings, name="load_settings"),
    path("api/save_settings", views_settings.save_plot_settings, name="save_settings"),
    path("api/download_plot", views_settings.download_plot, name="download_plot"),
    path("api/get_databases", views_settings.get_databases, name="get_databases"),
    path("api/upload_database", views_settings.database_upload, name="database_upload"),
    path("api/delete_database", views_settings.database_delete, name="database_delete"),
    path(
        "api/get_monomer_structure",
        views_settings.get_monomer_structure,
        name="get_monomer_structure",
    ),
    path(
        "api/upload_monomer_structure",
        views_settings.upload_monomer_structure,
        name="upload_monomer_structure",
    ),
    path(
        "api/delete_monomer_structure",
        views_settings.delete_monomer_structure,
        name="delete_monomer_structure",
    ),
    path(
        "api/get_multimer_structure",
        views_settings.get_multimer_structure,
        name="get_multimer_structure",
    ),
    path(
        "api/upload_multimer_structure",
        views_settings.upload_multimer_structure,
        name="upload_multimer_structure",
    ),
    path(
        "api/delete_multimer_structure",
        views_settings.delete_multimer_structure,
        name="delete_multimer_structure",
    ),
    path(
        "api/load_ptm_settings",
        views_settings.load_ptm_settings,
        name="load_ptm_settings",
    ),
    path(
        "api/load_default_ptm_settings_yaml",
        views_settings.load_default_ptm_settings_as_yaml,
        name="load_default_ptm_settings_yaml",
    ),
    path(
        "api/save_ptm_settings",
        views_settings.save_ptm_settings,
        name="save_ptm_settings",
    ),
    # catches all urls unknown to the backend to check if the frontend at index.html knows them - must be last url
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html")),
]
