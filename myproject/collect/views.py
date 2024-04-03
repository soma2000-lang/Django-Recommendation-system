from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from collector.models import Log
import datetime

from django.views.decorators.csrf import ensure_csrf_cookie