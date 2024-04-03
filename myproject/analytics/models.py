from django.db import models

# Create your models here.

class Ratings(models.Model):
    userId=models.CharField(max_length=16)
    rating=models.DecimalField(max_length=2)
    rating_timestamp=models.DateTimeField()
    time= models.CharField(max_length=8, default='explicit')
    
    def __str__(self) -> str:
        return "user_id: {}, movie_id: {}, rating: {}, type: {}"\
            .format(self.user_id, self.movie_id, self.rating, self.type)
    class Cluster(models.Model):
        cluster_id = models.IntegerField()
        user_id = models.IntegerField()

        def __str__(self):
            return "{} in {}".format(self.user_id, self.cluster_id)
