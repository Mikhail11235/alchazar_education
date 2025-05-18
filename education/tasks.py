import json
import redis
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .models import UserTestResult


User = get_user_model()


@shared_task
def update_user_ranks_and_top10():
    users_scores = (
        UserTestResult.objects.values('user')
        .annotate(total_score=Sum('max_score_first_3_attempts'))
        .order_by('-total_score')
    )
    rank_mapping = {}
    for index, data in enumerate(users_scores):
        user_id = data['user']
        if index < 10:
            rank_mapping[user_id] = 'Gold'
        elif index < 30:
            rank_mapping[user_id] = 'Silver'
        elif index < 100:
            rank_mapping[user_id] = 'Bronze'

    for user in User.objects.all():
        user.rank = rank_mapping.get(user.id, None)
        user.save()
    top_10_users = list(users_scores[:10])
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
    )
    r.set('top_10_users', json.dumps(top_10_users), ex=86400)
    return f"Updated {len(rank_mapping)} ranks and cached the top 10 users."
