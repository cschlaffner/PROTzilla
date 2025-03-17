from django.urls import include, path

from . import views

# TODO check if usable via api

app_name = "settings"
urlpatterns = [
    path("/", include("main.urls")),
    path("save", views.save, name="save"),
    path("last_view", views.last_view, name="last_view"),
    path("plots", views.settings_plots, name="settings_plots"),
    path("update_plot_preview", views.update_plot_preview, name="update_plot_preview"),
    path("databases", views.settings_databases, name="settings_databases")
]