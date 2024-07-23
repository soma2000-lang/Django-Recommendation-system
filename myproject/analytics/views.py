from django.shortcuts import render

# Create your views here.
import json
import decimal
import time
from datetime import datetime
from django.db import connection

from django.db import Count
from django.http import JsonResponse
from gensim import models
from movielovers.models import Movie, Genre
from reccommenders.models import SeededRecs, Similarity


def index(request):
    context_dict = {}
    return render(request, "analytics/index.html", context_dict)


def user(request, user_id):
    user_ratings = Rating.objects.filter(user_id=user_id).order_by("-rating")
    movies = Movie.objects.filter(movie_id__in=user_ratings.values("movie_id"))
    cluster = Cluster.objects.filter(user_id=user_id).first()

    ratings = {r.movie_id: r for r in user_ratings}
    movie = list()  # a list storing all the  movie
    if len(ratings) > 0:
        sum_of_ratings = sum([r.rating for r in ratings.values()])
        # now we will calculate the no of employees
        user_avg = sum_of_ratings / decimal.Decimal(len(ratings))
    else:  # noqa: E999
        user_avg = 0
    genres_ratings = {
        g["name"]: 0 for g in Genre.objects.all().values("name").distinct()
    }
    genres_count = {g["name"]: 0 for g in Genre.objects.all().values("name").distinct()}
    for movie in movies:
        id = movie.movie_id

        rating = ratings[id]

        r = rating.rating
        sum_rating += r
        movie_dtos.append(MovieDto(id, movie.title, r))
        for genre in movie.genres.all():
            if genre.name in genres_ratings.keys():
                genres_ratings[genre.name] += r - user_avg
                genres_count[genre.name] += 1
    max_value = max(genres_ratings.values())
    max_value = max(max_value, 1)

    def top_content(request):
        cursor = connection.cursor()
        cursor.execute(
            "SELECT \
                            content_id,\
                            mov.title,\
                            count(*) as sold\
                        FROM    collector_log log\
                        JOIN    moviegeeks_movie mov ON CAST(log.content_id AS INTEGER) = CAST(mov.movie_id AS INTEGER)\
                        WHERE 	event like 'buy' \
                        GROUP BY content_id, mov.title \
                        ORDER BY sold desc \
                        LIMIT 10"
        )
        data = dictfetchall(cursor)
        return JsonResponse(data, safe=False)

    def clusters(request):
        clusters_w_membercount = (
            Cluster.objects.values("cluster_id")
            .annotate(member_count=Count("user_id"))
            .order_by("cluster_id")
        )
        context_dict = {"cluster": list(clusters_w_membercount)}
        return JsonResponse(context_dict, safe=False)

    def similarity_graph(request):
        sim = Similarity.objects.all()[:10000]
        source_set = [s.source for s in sim]
        nodes = [{"id": s, "label": s} for s in set(source_set)]
        edges = [{"from": s.source, "to": s.target} for s in sim]
        print(nodes)
        print(edges)
        context_dict = {"nodes": nodes, "edges": edges}
        return render(request, "analytics/similarity_graph.html", context_dict)

    def get_api_key():
        # Load credentials
        cred = json.loads(open(".prs").read())
        return cred["themoviedb_apikey"]

    def get_statistics(request):
        date_timestamp = time.strptime(request.GET["date"], "%Y-%m-%d")

        end_date = datetime.fromtimestamp(time.mktime(date_timestamp))
        start_date = monthdelta(end_date, -1)

        print("getting statics for ", start_date, " and ", end_date)

        sessions_with_conversions = (
            Log.objects.filter(created__range=(start_date, end_date), event="buy")
            .values("session_id")
            .distinct()
        )
        buy_data = Log.objects.filter(
            created__range=(start_date, end_date), event="buy"
        ).values("event", "user_id", "content_id", "session_id")
        visitors = (
            Log.objects.filter(created__range=(start_date, end_date))
            .values("user_id")
            .distinct()
        )
        sessions = (
            Log.objects.filter(created__range=(start_date, end_date))
            .values("session_id")
            .distinct()
        )
        if len(sessions) == 0:
            conversions = 0
        else:
            conversions = (len(sessions_with_conversions) / len(sessions)) * 100
        conversions = round(conversions)
        return JsonResponse(
            {
                "items_sold": len(buy_data),
                "conversions": conversions,
                "visitors": len(visitors),
                "sessions": len(sessions),
            }
        )
    def events_on_conversions(request):
        cursor = connection.cursor()
        cursor.execute('''select
                            (case when c.conversion = 1 then \'Buy\' else \'No Buy\' end) as conversion,
                            event,
                                count(*) as count_items
                              FROM
                                    collector_log log
                              LEFT JOIN
                                (SELECT session_id, 1 as conversion
                                 FROM   collector_log
                                 WHERE  event=\'buy\') c
                                 ON     log.session_id = c.session_id
                               GROUP BY conversion, event''')
        data = dictfetchall(cursor)
        print(data)
        return JsonResponse(data, safe=False)
    class movie_rating():
        title = ""
        rating = 0

        def __init__(self, title, rating):
            self.title = title
            self.rating = rating

def monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
    if not m: m = 12  # noqa: E701
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)
