import os
import argparse
from decimal import Decimal

import logging
import numpy as np
from numpy import random
import pandas as pd
from django.db.models import Count
from sklearn.model_selection import KFold

from builder.bpr_calculator import BayesianPersonalizationRanking
from builder.fwls_calculator import FWLSCalculator
from builder.item_similarity_calculator import ItemSimilarityMatrixBuilder
from builder.matrix_factorization_calculator import MatrixFactorization
from evaluator.algorithm_evaluator import PrecisionAtK, MeanAverageError
from recs.bpr_recommender import BPRRecs
from recs.content_based_recommender import ContentBasedRecs
from recs.funksvd_recommender import FunkSVDRecs
from recs.fwls_recommender import FeatureWeightedLinearStacking
from recs.neighborhood_based_recommender import NeighborhoodBasedRecs
from recs.popularity_recommender import PopularityBasedRecs
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prs_project.settings")
import django
import time

django.setup()

from analytics.models import Rating
class EvaluationRunner(object):
    def __init__(self, folds, builder,
                 recommender,
                 k=10,
                 params=None,
                 logger=logging.getLogger('Evaluation runner')):
        self.folds = folds
        self.builder = builder
        self.recommender = recommender
        self.K = k
        self.params = params
        self.logger = logger
    def calculate(self, min_number_of_ratings=5, min_rank=10, number_test_users=-1):

        ratings_count = Rating.objects.all().count()
        self.logger.debug('{} ratings available'.format(ratings_count))

        if number_test_users == -1:
            ratings_rows = Rating.objects.all().values()
     def calculate_using_ratings_no_crossvalidation(self, all_ratings, min_number_of_ratings=5, min_rank=5):
            ratings = self.clean_data(all_ratings, min_number_of_ratings)

        users = ratings.user_id.unique()

        train_data_len = int((len(users) * 70 / 100))
        np.random.seed(42)
        np.random.shuffle(users)
        train_users, test_users = users[:train_data_len], users[train_data_len:]

        test_data, train_data = self.split_data(min_rank,
                                                ratings,
                                                test_users,
                                                train_users)

        self.logger.debug("Test run having {} training rows, and {} test rows".format(len(train_data),
                                                                          len(test_data)))
        
        if self.builder:
            if self.params:
                self.builder.build(train_data, self.params)
                self.logger.debug('setting save_path {}'.format(self.params['save_path']))
                self.recommender.set_save_path(self.params['save_path'])
            else:
                self.builder.build(train_data)
        self.logger.info("Build is finished")

        map, ar = PrecisionAtK(self.K, self.recommender).calculate_mean_average_precision(train_data, test_data)
        mae = 0
        results = {'map': map, 'ar': ar, 'mae': mae, 'users': len(users)}
        return results
        self.logger.info("Build is finished")

            map, ar = PrecisionAtK(self.K, self.recommender).calculate_mean_average_precision(train_data, test_data)
            mae = 0
            results = {'map': map, 'ar': ar, 'mae': mae, 'users': len(users)}
            return results


