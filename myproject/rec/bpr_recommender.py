import collections
import json
import pickle

import pandas as pd
from django.db.models import Avg

from analytics.models import Rating
from recs.base_recommender import base_recommender
class BPRRecs(base_recommender):
    def __init__(self, save_path='./models/bpr/'):
        self.save_path = save_path
        self.model_loaded = False
        self.avg = list(Rating.objects.all().aggregate(Avg('rating')).values())[0]

    def load_model(self, save_path):
        
            with open(save_path + 'item_bias.data', 'rb') as ub_file:
                self.item_bias = pickle.load(ub_file)
            with open(save_path + 'user_factors.json', 'r') as infile:
                self.user_factors = pd.DataFrame(json.load(infile)).T
            with open(save_path + 'item_factors.json', 'r') as infile:
                self.item_factors = pd.DataFrame(json.load(infile)).T
            self.ordered_item_bias = list(collections.OrderedDict(sorted(self.item_bias.items())).values())
            self.model_loaded = True