from django.shortcuts import render

import operator
from decimal import Decimal
from math import sqrt

import numpy as np
from django.db.models import Avg, Count
from django.http import JsonResponse
from analytics.models import Rating
from collect.models import Log
from movielovers.models import Movie
from reccommenders.models import SeededRecs
from rec.bpr_recommender import BPRRecs
from rec.content_based_recommender import ContentBasedRecs
from rec.funksvd_recommender import FunkSVDRecs
f

    def pearson(users, this_user, that_user):
        if this_user in users and that_user in users:
        this_user_avg = sum(users[this_user].values()) / len(users[this_user].values())
        that_user_avg = sum(users[that_user].values()) / len(users[that_user].values())

        all_movies = set(users[this_user].keys()) & set(users[that_user].keys())
        dividend = 0
        a_divisor = 0
        b_divisor = 0
        for movie in all_movies:
            if movie in users[this_user].keys() and movie in users[that_user].keys():
                a_nr = users[this_user][movie] - this_user_avg
                b_nr = users[that_user][movie] - that_user_avg
                dividend += a_nr * b_nr
                a_divisor += pow(a_nr, 2)
                b_divisor += pow(b_nr, 2)
        divisor = Decimal(sqrt(a_divisor) * sqrt(b_divisor))
        if divisor != 0:
            return dividend / Decimal(sqrt(a_divisor) * sqrt(b_divisor))

        return 0
    def jaccard(users, this_user, that_user):
        if this_user in users and that_user in users:
            intersect = set(users[this_user].keys()) & set(users[that_user].keys())

            union = set(users[this_user].keys()) | set(users[that_user].keys())

            return len(intersect) / Decimal(len(union))
        else:
            return 0
    def similar_users(request, user_id, sim_method):
        min = request.GET.get('min', 1)

        ratings = Rating.objects.filter(user_id=user_id)
        sim_users = Rating.objects.filter(movie_id__in=ratings.values('movie_id')) \
            .values('user_id') \
            .annotate(intersect=Count('user_id')).filter(intersect__gt=min)
        dataset = Rating.objects.filter(user_id__in=sim_users.values('user_id'))
        users = {u['user_id']: {} for u in sim_users}
        for row in dataset:
            if row.user_id in users.keys():
                users[row.user_id][row.movie_id] = row.rating
        similarity = dict()

    switcher = {
        'jaccard': jaccard,
        'pearson': pearson,

    }
    for user in sim_users:

        func = switcher.get(sim_method, lambda: "nothing")
        s = func(users, user_id, user['user_id'])

        if s > 0.2:
            similarity[user['user_id']] = round(s, 2)
    topn = sorted(similarity.items(), key=operator.itemgetter(1), reverse=True)[:10]
    
    # Ensemble methods, such as stacking, are designed to 
    # boost predictive accuracy by blending the predictions
    # of multiple machine learning models. its a linear technique,
    # Feature-Weighted Linear Stacking (FWLS), that incorporates meta-features for
    # improved accuracy while retaining the well-known virtues of linear regression
    # regarding speed, stability, and interpretability. FWLS combines model predictions 
    # linearly using coefficients that are themselves linear functions of meta-features.
    # This technique was a key facet of the solution of the second place team 
    # in the recently concluded Netflix Prize competition. Significant increases 
    # in accuracy over standard linear stacking are demonstrated on the Netflix 
    # Prize collaborative filtering dataset.

    def similar_content(request, content_id, num=6):

        sorted_items = ContentBasedRecs().seeded_rec([content_id], num)
        data = {
            'source_id': content_id,
            'data': sorted_items
        }

        return JsonResponse(data, safe=False)
   
    def recs_bpr(request, user_id, num=6):
        sorted_items = BPRRecs().recommend_items(user_id, num)

        data = {
            'user_id': user_id,
            'data': sorted_items
        }
        return JsonResponse(data, safe=False)


        return JsonResponse(data, safe=False)


    return JsonResponse(data, safe=False)
def lda2array(lda_vector, len):
    vec = np.zeros(len)
    for coor in lda_vector:
        if coor[0] > 1270:
            print("auc")
        vec[coor[0]] = coor[1]

    return vec

