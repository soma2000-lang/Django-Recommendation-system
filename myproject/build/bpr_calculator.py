
#implemention of bayesian personalization ranking
import os
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prs_project.settings")
import django
django.setup()

import pickle
from tqdm import tqdm
from datetime import datetime
from math import exp
import random
import pandas as pd
import numpy as np

from decimal import Decimal
from collections import defaultdict
from analytics.models import Rating

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger('BPR calculator')
class BayesianPersonalizationRanking(object):
    
    def __init__(self, save_path):
        self.learning_rate = 0.05
        self.bias_regularization = 0.002
        self.user_regularization = 0.005
        self.positive_item_regularization = 0.003
        self.negative_item_regularization = 0.0003
    def initialize_factors(self, train_data, k=25):
        self.ratings = train_data[['user_id', 'movie_id', 'rating']].as_matrix()
        self.k = k
        self.user_ids = pd.unique(train_data['user_id'])
        self.movie_ids = pd.unique(train_data['movie_id'])
        self.u_inx = {r: i for i, r in enumerate(self.user_ids)}
        self.i_inx = {r: i for i, r in enumerate(self.movie_ids)}
        


        self.user_factors = np.random.random_sample((len(self.user_ids), k))
        self.item_factors = np.random.random_sample((len(self.movie_ids), k))
        self.user_movies = train_data.groupby('user_id')['movie_id'].apply(lambda x: x.tolist()).to_dict()
        self.item_bias = defaultdict(lambda: 0)
        self.create_loss_samples()
    def build(self, ratings, params):
    
        if params:
            k = params['k']
            num_iterations = params['num_iterations']

        self.train(ratings, k, num_iterations)