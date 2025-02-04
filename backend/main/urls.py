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

# TODO R If you have views that handle API requests, you can import those here
# from myapp import views

urlpatterns = [
    path('', RedirectView.as_view(url='/static/index.html')),
    path("api/ping/", views.ping, name="ping"),
    path("api/jannesjsontest/", views.jannesjsontest, name="jannesjsontest"),
    path("api/plot/", views.plot, name="plot"),
    # TODO R API routes (if using Django for API)
    # path('api/', include('myapp.api.urls')),  # Example for API routes


    path("databases", views.databases, name="databases"),
    path("databases/upload", views.database_upload, name="database_upload"),
    path("databases/delete", views.database_delete, name="database_delete"),
    path("admin/", admin.site.urls),
]