import json
import shutil
from datetime import date

import pandas
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from backend.protzilla.constants.paths import EXTERNAL_DATA_PATH
from backend.protzilla.data_integration.database_query import uniprot_columns, uniprot_databases



# API to write csrf token into cookies via decorator
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"message": "CSRF cookie set."})

