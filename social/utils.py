
import random
import re
import random
from .models import Like, Post, UserProfile, Hashtag

def extract_and_assign_hashtags(post):
    hashtags = set(re.findall(r'#(\w+)', post.body))
    for tag in hashtags:
        hashtag_obj, _ = Hashtag.objects.get_or_create(name=tag.lower())
        post.hashtags.add(hashtag_obj)


import random
from django.db.models import Count, Case, When, IntegerField, F, ExpressionWrapper, FloatField, Q, Exists, OuterRef
from django.utils import timezone
from datetime import timedelta

def get_personalized_feed(user, limit=20):
    # Base query with all needed relations
    base_query = Post.objects.select_related('author')\
        .prefetch_related('likes', 'images', 'files', 'comments', 'group')
    
    now = timezone.now()
    like_subquery = Like.objects.filter(
        user=user,
        post=OuterRef('pk')
    )
    liked_posts = base_query.filter(likes__user=user)
    followed_users_posts = base_query.filter(author__in=user.profile.following.all())
    private_group_posts = base_query.filter(group__is_private=True, group__members=user)
    
    personalized_posts = (liked_posts | followed_users_posts | private_group_posts).distinct()
    personalized_posts = personalized_posts.annotate(
        like_count=Count('likes'),
        comment_count=Count('comments'),
        user_has_liked=Exists(like_subquery),
        hours_old=ExpressionWrapper(
            (now - F('created_on')) / timedelta(hours=1),
            output_field=FloatField()
        )
    )
    
    personalized_posts = personalized_posts.order_by('-created_on')
    
    return list(personalized_posts[:limit*2]) 

def get_random_posts(user, limit=200):
    now = timezone.now()
    
    like_subquery = Like.objects.filter(
        user=user,
        post=OuterRef('pk')
    )
    
    random_posts = Post.objects.select_related('author')\
        .prefetch_related('likes', 'images', 'files', 'comments')\
        .exclude(likes__user=user)\
        .exclude(author__in=user.profile.following.all())\
        .exclude(group__is_private=True, group__members=user)\
        .annotate(
            like_count=Count('likes'),
            comment_count=Count('comments'),
            user_has_liked=Exists(like_subquery),
            hours_old=ExpressionWrapper(
                (now - F('created_on')) / timedelta(hours=1),
                output_field=FloatField()
            )
        )
    
    trending_posts = random_posts.filter(
        created_on__gte=now - timedelta(days=7)
    ).order_by('-like_count', '-comment_count', '-created_on')[:limit]
    
    return list(trending_posts)

def calculate_post_score(post, user_id):
    recency_weight = max(1, 48 - min(post.hours_old, 48)) / 48 
    engagement_weight = (post.like_count + post.comment_count * 2) / 10
    relevance_weight = 2 if post.user_has_liked else 1
    media_weight = 0
    if hasattr(post, 'images') and post.images.exists():
        media_weight += 0.5
    if hasattr(post, 'files') and post.files.exists():
        media_weight += 0.3
    
    diversity_factor = 0.5 + random.random()
    
    score = (recency_weight * 2.5 + 
             engagement_weight * 1.5 + 
             relevance_weight * 3.0 +
             media_weight) * diversity_factor
    
    return score

def get_mixed_feed(user, limit=20):
    personalized_posts = get_personalized_feed(user, limit*2)
    random_posts = get_random_posts(user, limit*2)
    
    for post in personalized_posts + random_posts:
        post.score = calculate_post_score(post, user.id)
    
    all_scored_posts = sorted(personalized_posts + random_posts, 
                             key=lambda x: x.score, reverse=True)
    top_posts = all_scored_posts[:int(limit * 1.5)]
    selected_posts = random.sample(top_posts, min(int(limit * 0.65), len(top_posts)))
    
    remaining_posts = [p for p in all_scored_posts if p not in selected_posts]
    if remaining_posts:
        random_selection = random.sample(remaining_posts, 
                                        min(int(limit * 0.35), len(remaining_posts)))
        selected_posts.extend(random_selection)
    
    selected_posts = selected_posts[:limit]
    

    score_groups = {}
    for post in selected_posts:
        score_group = int(post.score * 5) / 5 
        if score_group not in score_groups:
            score_groups[score_group] = []
        score_groups[score_group].append(post)
    
    for group in score_groups.values():
        random.shuffle(group)
        
    final_feed = []
    for score in sorted(score_groups.keys(), reverse=True):
        final_feed.extend(score_groups[score])
    
    return final_feed


