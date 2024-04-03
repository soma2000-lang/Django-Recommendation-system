from django.shortcuts import render

# Create your views here.
import json
import decimal
import time
from datetime import datetime
from django.db import connection

from django.db import Count
from django.http import  JsonResponse
from gensim import models
from moviegeeks.models import Movie, Genre
from recommender.models import SeededRecs, Similarity


def index(request):
    context_dict = {}
    return render(request, 'analytics/index.html', context_dict)
