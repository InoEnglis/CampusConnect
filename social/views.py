import logging
from time import localtime
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View
from django.views.generic.edit import UpdateView, DeleteView
from django.db.models import Q
from django.http import HttpResponseNotFound, JsonResponse
from social.task import send_event_reminder
from .models import Feedback, GroupJoinRequest, Post, Comment, UserProfile, Group, Message, Notification, User, MessageStatus
from .forms import FeedbackForm, PostForm, CommentForm, GroupForm, ProfileSetupForm
from django.http import Http404
from .models import Post, PostImage, PostFile
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import Conversation, Message, MessageStatus, Like, SharedPost
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from itertools import chain
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib import messages
from .forms import ReportForm 
from django import forms
from .models import Post, SharedPost, Group, Event
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.db.models import Count, Case, When, IntegerField, F, ExpressionWrapper, FloatField, Q, Exists, OuterRef
from datetime import timedelta
import random
from .utils import extract_and_assign_hashtags, get_mixed_feed
from .forms import EventForm
from django.http import HttpResponse
from .models import Event, EventImage, EventFile
from .models import Rule

from django.shortcuts import get_object_or_404, redirect
from django.db.utils import IntegrityError
from .models import Conversation, User
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Group, GroupMembership, MutedUser
from django.contrib.auth.models import User
from django.shortcuts import redirect

from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Group, GroupMembership, MutedUser

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from .models import Group, GroupMembership, MutedUser



def conversation_search(request):
    query = request.GET.get('q', '')
    if not request.user.is_authenticated:
        return redirect('login')
    # Search for conversations where the logged-in user is a participant
    conversations = Conversation.objects.filter(
        Q(participants=request.user)  # User must be a participant
    )

    # Further filter by search query if it exists
    if query:
        conversations = conversations.filter(name__icontains=query) 

    return render(request, 'social/conversation_search_result.html', {'results': conversations, 'query': query})


def user_list_view(request):
    users = User.objects.all()  
    context = {
        'title': 'User List',
        'description': 'A list of all registered users.',
        'users': users,
    }
    return render(request, 'social/user_list.html', context)


@csrf_exempt
def send_message(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if the user is a participant in the conversation
    if request.user not in conversation.participants.all():
        return JsonResponse({"error": "Permission denied"}, status=403)
    
    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            message = Message.objects.create(conversation=conversation, sender=request.user, content=body)
            print(f"Message created: {message}")
            
            for participant in conversation.participants.all():
                print(f"Creating MessageStatus for participant: {participant}")
                MessageStatus.objects.create(
                    message=message,
                    user=participant,
                    is_read=False  
                )
            
            return JsonResponse({
                "sender": message.sender.username,
                "body": message.content,
                "timestamp": message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "message_id": message.id
            })
        return JsonResponse({"error": "Message body cannot be empty"}, status=400)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)


from django.utils import timezone

def mark_message_as_read(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        message_status = MessageStatus.objects.get(message=message, user=request.user)
        message_status.is_read = True
        message_status.read_at = timezone.now()  
        message_status.save()
        print(f"Message {message_id} marked as read.")
    except MessageStatus.DoesNotExist:

        pass


def get_unread_message_count(request):
    if request.user.is_authenticated:
        unread_count = MessageStatus.objects.filter(user=request.user, is_read=False).count()
        print(f"Unread messages count: {unread_count}")
    else:
        unread_count = 0
    return JsonResponse({"unread_count": unread_count})


@login_required
def navbar_view(request):
    if request.user.is_authenticated:
        unread_messages_count = get_unread_message_count(request.user)
        unread_notifications_count = Notification.objects.filter(user=request.user, read=False).count()
    else:
        unread_messages_count = 0
        unread_notifications_count = 0

    return render(request, "landing/navbar.html", {
        "unread_messages_count": unread_messages_count,
        "unread_notifications_count": unread_notifications_count,
    })


def get_unread_notifications_count(user):
    return Notification.objects.filter(user=user, read=False).count()

@login_required
def unread_notifications_count(request):
    unread_notifications_count = get_unread_notifications_count(request.user)
    return JsonResponse({'unread_count': unread_notifications_count})


from django.shortcuts import render
from .models import Conversation, User
from django.db.models import Q

from django.shortcuts import render
from .models import Conversation, User
from django.db.models import Q
from django.db import models
from django.shortcuts import render
from .models import Conversation, User
from django.shortcuts import render
from .models import Conversation, User

from django.db import models  # Make sure this is imported!
from django.db.models import Count, Q

from django.db.models import Count, Q, OuterRef, Subquery

from django.db.models import Count, Q, OuterRef, Subquery
from django.shortcuts import render
from .models import MessageStatus, Conversation, Message

from django.db.models import Subquery, OuterRef, Count, Q
from django.utils import timezone
from django.shortcuts import render
from .models import Conversation, Message, MessageStatus, User

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Conversation, Message, MessageStatus

from django.db.models import Count, Q, F
from django.shortcuts import render

from django.db.models import Count, Q, Subquery, OuterRef
from django.utils import timezone

def conversation_list(request):
    # Get all conversations where the user is a participant
    conversations = Conversation.objects.filter(participants=request.user)

    # Annotate the latest message timestamp and unread message count
    conversations = conversations.annotate(
        latest_message_time=Subquery(
            Message.objects.filter(conversation=OuterRef('pk'))
            .order_by('-timestamp')
            .values('timestamp')[:1]
        )
    )

    conversations = conversations.annotate(
        unread_count=Count(
            'conversation_messages',
            filter=Q(conversation_messages__message_statuses__user=request.user,
                     conversation_messages__message_statuses__is_read=False)
        )
    )

    # Order conversations by latest message timestamp
    conversations = conversations.order_by('-latest_message_time')

    # Get all users
    users = User.objects.all()

    # Get global chat
    global_chat = Conversation.objects.filter(type='global').first()

    # Get receiver info and online status for private conversations
    for conversation in conversations:
        conversation.online_status = False
        conversation.conversation_name = conversation.get_conversation_name(request.user)

        if conversation.type == 'private':
            receiver = conversation.participants.exclude(id=request.user.id).first()
            if receiver:
                conversation.receiver_name = receiver.profile.name if receiver.profile.name else receiver.username
                conversation.receiver_profile_pic = receiver.profile.picture.url if receiver.profile.picture else None
                if hasattr(receiver, 'userstatus') and receiver.userstatus.is_online:
                    conversation.online_status = True

        elif conversation.type == 'global':
            for participant in conversation.participants.all():
                if hasattr(participant, 'userstatus') and participant.userstatus.is_online:
                    conversation.online_status = True
                    break

        # Mark messages as read if they haven't been read yet
        # For each message in the conversation, mark it as read
        for message in conversation.conversation_messages.all():
            message_status = MessageStatus.objects.filter(message=message, user=request.user, is_read=False)
            if message_status.exists():
                # Mark the message as read
                message_status.update(is_read=True, read_at=timezone.now())

    # Set global chat name
    global_chat_name = global_chat.get_conversation_name(request.user) if global_chat else "Global Chat"

    # Prepare context for rendering
    context = {
        'conversations': conversations,
        'global_chat': global_chat,
        'global_chat_name': global_chat_name,
        'users': users,
    }

    return render(request, 'social/conversation_list.html', context)


def open_conversation(request, conversation_id):
    # Fetch the conversation the user is trying to open
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Fetch messages associated with the conversation using the correct related name
    messages = conversation.conversation_messages.all()

    # Mark all messages as read for the current user
    for message in messages:
        message_status = MessageStatus.objects.filter(message=message, user=request.user).first()
        if message_status and not message_status.is_read:
            message_status.is_read = True
            message_status.read_at = timezone.now()
            message_status.save()

    context = {
        'conversation': conversation,
        'messages': messages,
        'is_conversation_open': True,  # Add this to flag the opened conversation
    }

    return render(request, 'social/open_conversation.html', context)

class PostListView(LoginRequiredMixin, View):
    def get_combined_posts(self, user):
        # Get posts with enhanced analytics
        personalized_posts = get_mixed_feed(user, limit=20)
        shared_posts = SharedPost.objects.all().select_related('original_post', 'shared_by').order_by('-shared_on')
        
        post_ids = set()
        combined_posts = []
        
        # Create a subquery to check if the user has liked each post
        like_subquery = Like.objects.filter(
            user=user,
            post=OuterRef('pk')
        )
        
        # Add personalized posts with score information
        for post in personalized_posts:
            if post.id not in post_ids:
                post_score = getattr(post, 'score', None)
                
                fresh_post = Post.objects.filter(id=post.id).select_related(
                    'author', 'group', 'author__profile'
                ).prefetch_related('images', 'comments', 'likes').annotate(
                    user_has_liked=Exists(like_subquery)
                ).first()
                
                if fresh_post:
                    if post_score is not None:
                        fresh_post.score = post_score
                    combined_posts.append({'type': 'post', 'data': fresh_post})  
                    post_ids.add(post.id)
        for shared_post in shared_posts:
            if shared_post.original_post.id not in post_ids:
                original_like_subquery = Like.objects.filter(
                    user=user,
                    post=OuterRef('original_post__pk')
                )
                
                fresh_shared_post = SharedPost.objects.filter(id=shared_post.id).select_related(
                    'original_post', 'shared_by', 'original_post__author', 'original_post__group'
                ).prefetch_related('original_post__images', 'original_post__comments', 'original_post__likes').first()
                
                if fresh_shared_post:
                    original_post_has_like = Like.objects.filter(
                        user=user, 
                        post=fresh_shared_post.original_post
                    ).exists()
                    
                    now = timezone.now()
                    hours_old = (now - fresh_shared_post.shared_on).total_seconds() / 3600
                    
                    like_count = fresh_shared_post.original_post.likes.count()
                    comment_count = fresh_shared_post.original_post.comments.count() if hasattr(fresh_shared_post.original_post, 'comments') else 0
                
                    recency_weight = max(1, 48 - min(hours_old, 48)) / 48
                    engagement_weight = (like_count + comment_count * 2) / 10
                    relevance_weight = 2 if original_post_has_like else 1
                    
                    diversity_factor = 0.5 + random.random()
                    
                    fresh_shared_post.score = (recency_weight * 2.5 + 
                                              engagement_weight * 1.5 + 
                                              relevance_weight * 3.0) * diversity_factor
                    
                    fresh_shared_post.original_post.user_has_liked = original_post_has_like
                    
                    combined_posts.append({'type': 'shared_post', 'data': fresh_shared_post})
                    post_ids.add(shared_post.original_post.id)
        

        now = timezone.now()
        
        group_posts = Post.objects.filter(
            group__isnull=False,
            group__members=user  
        ).select_related('author', 'group', 'author__profile').prefetch_related('images', 'comments', 'likes').annotate(
            like_count=Count('likes'),
            comment_count=Count('comments'),
            user_has_liked=Exists(like_subquery),
            hours_old=ExpressionWrapper(
                (now - F('created_on')) / timedelta(hours=1),
                output_field=FloatField()
            )
        )
        
        for post in group_posts:
            if post.id not in post_ids:
                # Calculate score for this group post
                recency_weight = max(1, 48 - min(post.hours_old, 48)) / 48
                engagement_weight = (post.like_count + post.comment_count * 2) / 10
                relevance_weight = 2 if post.user_has_liked else 1
                
                # Add weight for media content
                media_weight = 0
                if hasattr(post, 'images') and post.images.exists():
                    media_weight += 0.5
                if hasattr(post, 'files') and post.files.exists():
                    media_weight += 0.3
                
                diversity_factor = 0.5 + random.random()
                
                post.score = (recency_weight * 2.5 + 
                             engagement_weight * 1.5 + 
                             relevance_weight * 3.0 +
                             media_weight) * diversity_factor
                
                combined_posts.append({'type': 'post', 'data': post})
                post_ids.add(post.id)
        
        # Sort the combined posts by score first, then by date for items with similar scores
        combined_posts = sorted(
            combined_posts,
            key=lambda x: (
                getattr(x['data'], 'score', 0),
                x['data'].created_on if x['type'] == 'post' else x['data'].shared_on
            ),
            reverse=True
        )
        
        return combined_posts

    def get(self, request, *args, **kwargs):
        user = request.user
        combined_posts = self.get_combined_posts(user)

        # Paginator setup
        paginator = Paginator(combined_posts, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get groups, events, and other data for the sidebar
        public_groups = Group.objects.filter(is_private=False)
        private_groups = Group.objects.filter(is_private=True, members=user)
        groups = (public_groups | private_groups).distinct()[:5]

        user_profile = request.user.profile
        followers = UserProfile.objects.filter(user__in=user_profile.followers.all())[:5]
        followed_users = UserProfile.objects.filter(followers=request.user)[:5]
        events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:20]
        rules = Rule.objects.all()

        # Prepare the context for rendering
        context = {
            'combined_posts': page_obj,
            'form': PostForm(),
            'public_groups': public_groups,
            'private_groups': private_groups,
            'groups': groups,
            'events': events,
            'followers': followers,
            'followed_users': followed_users,
            'rules': rules,
            'feedback_form': FeedbackForm(),
        }
        return render(request, 'social/post_list.html', context)

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        files = request.FILES.getlist('files')

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()

            # Assign hashtags if applicable
            extract_and_assign_hashtags(new_post)

            # Save images and files for the post
            for image in images:
                PostImage.objects.create(post=new_post, image=image)
            for file in files:
                PostFile.objects.create(post=new_post, file=file)

            return redirect('post-list')

        # If form is invalid, rerender the page with the form errors
        user = request.user
        combined_posts = self.get_combined_posts(user)

        # Paginator setup for posts
        paginator = Paginator(combined_posts, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get groups, events, and other data for the sidebar
        public_groups = Group.objects.filter(is_private=False)
        private_groups = Group.objects.filter(is_private=True, members=user)
        groups = (public_groups | private_groups).distinct()[:5]

        user_profile = request.user.profile
        followers = UserProfile.objects.filter(user__in=user_profile.followers.all())[:5]
        followed_users = UserProfile.objects.filter(followers=request.user)[:5]
        events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:5]
        rules = Rule.objects.all()

        # Prepare the context for rendering
        context = {
            'combined_posts': page_obj,
            'form': form,  
            'public_groups': public_groups,
            'private_groups': private_groups,
            'groups': groups,
            'events': events,
            'followers': followers,
            'followed_users': followed_users,
            'rules': rules,
            'feedback_form': FeedbackForm(),
        }
        return render(request, 'social/post_list.html', context)


from django.views.generic import ListView

class HashtagPostListView(ListView):
    model = Post
    template_name = 'social/hashtag_posts_new.html'  # Updated template
    context_object_name = 'posts'

    def get_queryset(self):
        hashtag_name = self.kwargs['hashtag_name'].lower()
        hashtag = Hashtag.objects.filter(name__iexact=hashtag_name).first()
        if hashtag:
            return Post.objects.filter(hashtags=hashtag).order_by('-created_on')
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hashtag_name = self.kwargs['hashtag_name']
        context['hashtag_name'] = hashtag_name

        # Get the count of posts for each hashtag and rank them
        context['post_count'] = Post.objects.filter(hashtags__name__iexact=hashtag_name).count()

        # Get the top 10 hashtags ranked by usage
        top_hashtags = Hashtag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:10]
        context['top_hashtags'] = top_hashtags

        context['groups'] = Group.objects.all()

        # Add default profile image if not set
        for group in context['groups']:
            if not group.profile_image:
                group.profile_image = 'uploads/group_images/default_profile_image.jpg'

        return context


class GetLatestPostsView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Prefetch related images for posts to avoid lazy loading issues
            posts = Post.objects.prefetch_related('images').order_by('-created_on')
            
            paginator = Paginator(posts, 5)  
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            # Render posts
            rendered_posts = [
                render_to_string('social/post_card.html', {'post': post}, request)
                for post in page_obj.object_list
            ]

            return JsonResponse({
                'posts': rendered_posts,
                'has_next': page_obj.has_next(),
            })
        except Exception as e:
            # Log the error for easier debugging
            print(f"Error in GetLatestPostsView: {str(e)}")
            return JsonResponse({'error': 'An error occurred while loading posts.'}, status=500)



class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404("Post not found")
        
        form = CommentForm()
        comments = Comment.objects.filter(post=post, parent=None).order_by('-created_on')  
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        print(context) 
        return render(request, 'social/post_detail.html', context)


    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id') 
            parent_comment = Comment.objects.get(id=parent_id) if parent_id else None
            
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()
            
            comment_data = {
                'comment': new_comment.comment,
                'author': new_comment.author.username,
                'created_on': new_comment.created_on.strftime('%Y-%m-%d %H:%M:%S'),
                'parent_id': parent_id,
            }
            return JsonResponse(comment_data)

        comments = Comment.objects.filter(post=post, parent=None).order_by('-created_on')
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        return render(request, 'social/post_detail.html', context)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body', 'image']
    template_name = 'social/post_edit.html'

    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        return self.request.user == self.get_object().author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        return self.request.user == self.get_object().author

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'

    def get_success_url(self):
    
        return reverse_lazy('post-detail', kwargs={'pk': self.kwargs['post_pk']})

    def test_func(self):
        return self.request.user == self.get_object().author


class ProfileView(View):
    def get(self, request, pk):
        # 1) Get the user instance using the primary key (pk)
        user = get_object_or_404(User, pk=pk)
        
        # 2) Try to get the user profile
        try:
            user_profile = user.profile  # Assuming you have a related profile
        except AttributeError:
            return render(request, 'social/profile_not_found.html')

        # 3) Fetch posts by this user (author is a ForeignKey to User model)
        posts = Post.objects.filter(author=user).order_by('-created_on')  

        # 4) Render the profile page with the user profile and posts
        return render(request, 'social/profile.html', {
            'user_profile': user_profile,
            'posts': posts,
        })



class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = [
        'first_name', 'middle_name', 'last_name', 'extension',
        'name', 'bio', 'birth_date', 'picture',
        'section', 'year_level', 'course', 'department',
        'province', 'municipality', 'barangay', 'street',
        'current_work'
    ]
    template_name = 'social/profile_edit.html'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        return self.request.user == self.get_object().user


class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
        return redirect('profile', pk=pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        return redirect('profile', pk=pk)

class SearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        active_tab = request.GET.get('tab', 'all')

        post_results = Post.objects.none()
        comment_results = Comment.objects.none()
        profile_results = UserProfile.objects.none()
        group_results = Group.objects.none()

        if query:
            if active_tab == 'all':
                post_results = Post.objects.filter(
                    Q(body__icontains=query) |
                    Q(author__username__icontains=query)
                )
                comment_results = Comment.objects.filter(
                    Q(comment__icontains=query) |
                    Q(author__username__icontains=query)
                )
                profile_results = UserProfile.objects.filter(
                    Q(name__icontains=query) |
                    Q(bio__icontains=query) |
                    Q(user__username__icontains=query)
                )
                group_results = Group.objects.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query)
                )

            elif active_tab == 'followers':
                user = request.user
                followed_profiles = UserProfile.objects.filter(followers=user)
                profile_results = followed_profiles.filter(
                    Q(name__icontains=query) |
                    Q(user__username__icontains=query)
                )

            elif active_tab == 'groups':
                group_results = Group.objects.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query)
                )

            elif active_tab == 'recents':
                post_results = Post.objects.filter(
                    Q(body__icontains=query) |
                    Q(author__username__icontains=query)
                ).order_by('-created_on')[:10]
                comment_results = Comment.objects.filter(
                    Q(comment__icontains=query) |
                    Q(author__username__icontains=query)
                ).order_by('-created_on')[:10]

        context = {
            'query': query,
            'active_tab': active_tab,
            'post_results': post_results,
            'comment_results': comment_results,
            'profile_results': profile_results,
            'group_results': group_results,
        }
        return render(request, 'social/search_results.html', context)



def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            print("Form is valid")  
            form.save()
            return redirect('group_list')  
        else:
            print("Form is not valid") 
            print(form.errors)  
    else:
        form = GroupForm(user=request.user)
    
    return render(request, 'groups/create_group.html', {'form': form})

def group_list(request):
    # Fetch public and private groups as before
    public_groups = Group.objects.filter(is_private=False)
    private_groups = Group.objects.filter(is_private=True)
    all_groups = list(chain(public_groups, private_groups))
    random.shuffle(all_groups) 
    
    pending_requests = {}
    for group in private_groups:
        pending_requests[group.id] = group.join_requests_set.filter(user=request.user).exists()

    # NEW: Get groups where the user is a member
    user_groups = Group.objects.filter(members=request.user)

    # NEW: Get the filter parameter from the GET request (default to 'trending')
    filter_type = request.GET.get('filter', 'trending')  
    
    # Apply filters based on the chosen filter type
    if filter_type == 'trending':
        filtered_groups = Group.objects.order_by('-created_at')  
    elif filter_type == 'top':
        filtered_groups = Group.objects.annotate(num_members=Count('members')).order_by('-num_members')  #
    elif filter_type == 'fresh':
        filtered_groups = Group.objects.order_by('-created_at') 
    else:
        filtered_groups = Group.objects.all()  

    # Split the filtered groups into public and private
    public_filtered_groups = filtered_groups.filter(is_private=False)
    private_filtered_groups = filtered_groups.filter(is_private=True)

    # Handle group creation
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('group_list')  
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = GroupForm(user=request.user)

    context = {
        'public_groups': public_groups,
        'private_groups': private_groups,
        'pending_requests': pending_requests,
        'form': form,
        'all_groups': all_groups,
        'user_groups': user_groups,
        'filtered_groups': filtered_groups,  
        'filter': filter_type,  
    }

    return render(request, 'groups/group_list.html', context)


def about_view(request):
    return render(request, 'social/about.html')


@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user in group.members.all():
        group.members.remove(request.user)
        messages.success(request, f"You have left the group '{group.name}'.")
    else:
        messages.info(request, "You are not a member of this group.")

    return redirect('group_list') 

@login_required
def group_detail(request, group_id):
   
    group = get_object_or_404(Group, id=group_id)
    rules = group.rules.all() 
    pending_request = None 
    pending_requests = [] 
    rule_form = None  
    posts = []  
    
    user = request.user
    is_authenticated = user.is_authenticated
    is_admin = is_authenticated and group.is_admin(user)  
    is_member = is_authenticated and user in group.members.all() 
    moderators = User.objects.filter(
    id__in=GroupMembership.objects.filter(group=group, role='moderator').values_list('user_id', flat=True)
)

    if not group.is_private or is_member or is_admin:
        posts = Post.objects.filter(group=group).order_by('-created_on').prefetch_related('images')
    
    if is_authenticated:
        pending_request = GroupJoinRequest.objects.filter(group=group, user=user, status='pending').first()

        if is_admin:
            pending_requests = GroupJoinRequest.objects.filter(group=group, status='pending')
            rule_form = GroupRuleForm()

            if request.method == 'POST' and 'create_rule' in request.POST:
                rule_form = GroupRuleForm(request.POST)
                if rule_form.is_valid():
                    rule = rule_form.save(commit=False)
                    rule.group = group  # Assign the group to the rule
                    rule.save()  # Save the rule
                    messages.success(request, "Rule created successfully.")
                    return redirect('group_detail', group_id=group.id)

        # Handle post creation logic if the form is submitted
        if request.method == 'POST' and 'create_post' in request.POST:
            body = request.POST.get('body')
            images = request.FILES.getlist('images')  
            
            if body:
                post = Post.objects.create(
                    author=user,
                    group=group,
                    body=body,
                )
                for image in images:
                    PostImage.objects.create(post=post, image=image)
                
                messages.success(request, "Post created successfully.")
                return redirect('group_detail', group_id=group.id)  
            else:
                messages.error(request, "Post content cannot be empty.")  
    
    context = {
        'group': group,
        'posts': posts,
        'rules': rules,
        'rule_form': rule_form,
        'pending_request': pending_request,
        'pending_requests': pending_requests,
        'is_member': is_member,
        'is_admin': is_admin,
        'moderators': moderators,
    }
    return render(request, 'groups/group_detail.html', context)

def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Already a member
    if request.user in group.members.all():
        return redirect('group_detail', group_id=group.id)

    join_request = GroupJoinRequest.objects.filter(user=request.user, group=group).first()

    if group.is_private:
        if group.join_mode == 'auto':
            group.members.add(request.user)
            # Update or create a join request with status approved
            if join_request:
                join_request.status = 'approved'
                join_request.save()
            else:
                GroupJoinRequest.objects.create(user=request.user, group=group, status='approved')
            messages.success(request, f"You have automatically joined the private group '{group.name}'.")
        else:
            if join_request:
                if join_request.status in ['rejected', 'approved']:
                    join_request.status = 'pending'
                    join_request.save()
                    messages.success(request, "Join request re-submitted. Please wait for admin approval.")
                else:
                    messages.info(request, f"Your join request is already {join_request.status}.")
            else:
                GroupJoinRequest.objects.create(user=request.user, group=group, status='pending')
                messages.success(request, "Join request sent! Please wait for admin approval.")
        return redirect('group_detail', group_id=group.id)
    else:
        # Public group: just add
        group.members.add(request.user)
        if join_request:
            join_request.status = 'approved'
            join_request.save()
        else:
            GroupJoinRequest.objects.create(user=request.user, group=group, status='approved')
        messages.success(request, f"You have joined the public group '{group.name}'.")
        return redirect('group_detail', group_id=group.id)


    
def admin_approval(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Ensure that the user is an admin or creator of the group
    if not group.is_admin(request.user):
        messages.error(request, "You don't have permission to manage join requests.")
        return redirect('group_list')

    # Get all pending join requests
    pending_requests = group.join_requests_set.filter(status='pending')

    # Users and roles
    members = group.members.all()
    banned_users = group.banned_users.all()
    muted_users = MutedUser.objects.filter(group=group)

    moderator_ids = set(
        GroupMembership.objects.filter(group=group, role='moderator')
        .values_list('user_id', flat=True)
    )
    banned_ids = set(banned_users.values_list('id', flat=True))
    muted_ids = set(muted_users.values_list('user_id', flat=True))

    if request.method == 'POST':
        action = request.POST.get('action')
        request_id = request.POST.get('request_id')
        join_request = get_object_or_404(GroupJoinRequest, id=request_id)

        if join_request.status == 'approved':
            messages.info(request, f"{join_request.user.username} has already been approved.")
        elif join_request.status == 'rejected':
            if action == 'approve':
                join_request.status = 'approved'
                group.members.add(join_request.user)
                messages.success(request, f"{join_request.user.username} has been approved to join the group.")
                join_request.save()
            else:
                messages.info(request, f"{join_request.user.username}'s request was already rejected.")
        else:
            if action == 'approve':
                join_request.status = 'approved'
                group.members.add(join_request.user)
                messages.success(request, f"{join_request.user.username} has been approved to join the group.")
            elif action == 'reject':
                join_request.status = 'rejected'
                messages.success(request, f"{join_request.user.username}'s request has been rejected.")
            join_request.save()

        return redirect('admin_approval', group_id=group.id)

    context = {
        'group': group,
        'pending_requests': pending_requests,
        'members': members,
        'banned_users': banned_users,
        'muted_users': muted_users,
        'banned_ids': banned_ids,
        'muted_ids': muted_ids,
        'moderator_ids': moderator_ids,
    }

    return render(request, 'groups/admin_approval.html', context)


@login_required
def group_settings(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Check if the user is an admin of the group
    if not group.is_admin(request.user):
        return redirect('home')  
    
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_settings', group_id=group.id)  
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'groups/group_settings.html', {'form': form, 'group': group})




def manage_users(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all()
    banned_users = group.banned_users.all()
    muted_users = MutedUser.objects.filter(group=group)

    # Get user roles
    moderator_ids = set(
        GroupMembership.objects.filter(group=group, role='moderator')
        .values_list('user_id', flat=True)
    )
    banned_ids = set(banned_users.values_list('id', flat=True))
    muted_ids = set(muted_users.values_list('user_id', flat=True))

    if request.method == "POST":
        action_data = request.POST.get('action', '')
        if '-' in action_data:
            action, user_id = action_data.split('-', 1)
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return HttpResponseNotFound("User not found")

            # Block changes to self, creator, or admins
            if user == request.user or user == group.creator or user in group.admins.all():
                messages.error(request, "You can't perform this action on yourself, the group creator, or another admin.")
                return redirect('manage_users', group_id=group.id)

            if action == "kick":
                group.members.remove(user)
                GroupMembership.objects.filter(group=group, user=user).delete()
                messages.success(request, f"{user.username} has been kicked.")
            elif action == "ban":
                group.banned_users.add(user)
                group.members.remove(user)
                MutedUser.objects.filter(group=group, user=user).delete()
                GroupMembership.objects.filter(group=group, user=user).delete()
                messages.success(request, f"{user.username} has been banned.")
            elif action == "unban":
                group.banned_users.remove(user)
                group.members.add(user)
                messages.success(request, f"{user.username} has been unbanned.")
            elif action == "mute":
                MutedUser.objects.get_or_create(group=group, user=user)
                messages.success(request, f"{user.username} has been muted.")
            elif action == "unmute":
                MutedUser.objects.filter(group=group, user=user).delete()
                messages.success(request, f"{user.username} has been unmuted.")
            elif action == "promote":
                GroupMembership.objects.update_or_create(
                    group=group, user=user, defaults={"role": "moderator"}
                )
                messages.success(request, f"{user.username} has been promoted to moderator.")
            elif action == "demote":
                GroupMembership.objects.filter(group=group, user=user).update(role="member")
                messages.success(request, f"{user.username} has been demoted to member.")

            return redirect('manage_users', group_id=group.id)

    return render(request, 'groups/manage_users.html', {
        'group': group,
        'members': members,
        'banned_users': banned_users,
        'muted_users': muted_users,
        'banned_ids': banned_ids,
        'muted_ids': muted_ids,
        'moderator_ids': moderator_ids,
    })


    context = {
        'group': group,
        'members': members,
        'banned_ids': banned_ids,
        'muted_ids': muted_ids,
        'moderator_ids': moderator_ids,
        'banned_users': banned_users,
        'muted_users': muted_users,
    }
    return render(request, 'groups/manage_users.html', context)


@login_required
def notifications_api(request):
    page = request.GET.get('page', 1)  # Current page number
    notifications = Notification.objects.filter(user=request.user, read=False).order_by('-timestamp')
    paginator = Paginator(notifications, 10)  
    notifications_page = paginator.get_page(page)

    notifications_data = [
        {
            'id': notification.id,
            'message': notification.message,
            'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for notification in notifications_page
    ]

    return JsonResponse({
        'notifications': notifications_data,
        'has_next': notifications_page.has_next(),
        'has_previous': notifications_page.has_previous(),
    })


@login_required
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

@login_required
def notifications_page(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    notifications.filter(read=False).update(read=True, read_at=timezone.now())
    
    return render(request, 'social/notification-page.html', {'notifications': notifications})




from django.urls import reverse

@login_required
def toggle_like(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()  
            liked = False
        else:
            liked = True
            if request.user != post.author:
                Notification.objects.create(
                    user=post.author,
                    sender=request.user,
                    post=post,
                    notification_type='like',
                    message=f'Your post "{post.body[:20]}" has been liked by {request.user.username}.',
                    timestamp=timezone.now(),
                    read=False,
                    link=reverse('post-detail', kwargs={'pk': post.pk}) 
                )

        return JsonResponse({
            'liked': liked,
            'like_count': post.likes.count(),
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)




@login_required
def share_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)

        # Check if the user has already shared this post
        if SharedPost.objects.filter(shared_by=request.user, original_post=post).exists():
            return JsonResponse({'success': False, 'error': 'You have already shared this post.'}, status=400)

        # Optional comment added during sharing
        shared_comment = request.POST.get('shared_comment', '')

        # Create a new shared post
        shared_post = SharedPost.objects.create(
            original_post=post,
            shared_by=request.user,
            shared_comment=shared_comment
        )
        if request.user != post.author:  
            Notification.objects.create(
                user=post.author, 
                sender=request.user,  
                post=post,
                notification_type='share',
                message=f"{request.user.username} shared your post.",
                read=False,
                link=reverse('post-detail', kwargs={'pk': post.pk})
            )

        # Return the success response with the shared post URL
        return JsonResponse({
            'success': True,
            'message': 'Post shared successfully!',
            'shared_post_url': shared_post.get_absolute_url() 
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@receiver(post_save, sender=Comment)
def create_reply_notification(sender, instance, created, **kwargs):
    # Check if the comment is a reply
    if created and instance.parent:
        parent_comment = instance.parent  
        
        notified_user = parent_comment.author
   
        if notified_user != instance.author:  
            Notification.objects.create(
                user=notified_user,
                sender=instance.author,
                post=instance.post,  # Use instance.post instead of post
                notification_type='comment',  
                message=f"{instance.author.username} replied to your comment.",
                read=False,
                link=reverse('post-detail', kwargs={'pk': instance.post.pk})  
            )
            



# reporting view
def report_post(request, post_id):
    # Get the post that needs to be reported
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        # Handle the form submission
        form = ReportForm(request.POST)
        if form.is_valid():
            # Save the report (could be a new model or a simple flag on the Post)
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user  # Correct field name for user who reported it
            report.save()

            # Notify the admin (this could be an email, a message, or a notification system)
            messages.success(request, "Thank you for reporting this post. Our team will review it shortly.")
            
            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Your report has been submitted successfully.'})

        else:
            return JsonResponse({'status': 'error', 'message': 'There was an issue with your report.'}, status=400)

    else:
        form = ReportForm()

    return render(request, 'social/report_post.html', {
        'form': form,
        'post': post,
        'is_report_page': True  
    })

# banning
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if user.profile.is_banned:
            return redirect('banned_user')  
        return super().form_valid(form)

def banned_user(request):
    """View for banned users."""
    return render(request, 'social/banned_user.html', {})

from allauth.account.views import AccountInactiveView
from django.views.generic import TemplateView

class BannedUserView(TemplateView):
    template_name = 'social/banned_user.html'

# events
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the event and set the creator to the logged-in user
            event = form.save(commit=False)  
            event.created_by = request.user  
            event.save()  

            images = request.FILES.getlist('images')
            for image in images:
                event.images.create(image=image)

            # Handle video file if available
            if 'video_file' in request.FILES:
                event.video_file = request.FILES['video_file']
                event.save()

            # Redirect to event list or event detail page
            return redirect('event_list')  

    else:
        form = EventForm()

    return render(request, 'social/create_event.html', {'form': form})


from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator


def event_list(request):
    events = Event.objects.all().order_by('-date')

    # Fetch unread notifications for the current user
    notifications = Notification.objects.filter(user=request.user, read=False)

    return render(request, 'social/event_list.html', {
        'events': events,
        'notifications': notifications,
    })

    
  

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    notifications = Notification.objects.filter(user=request.user, read=False)

    return render(request, 'social/event_detail.html', {
        'event': event,
        'notifications': notifications,
    })



# follower
@login_required
def follower_list(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    followers = profile.followers.all()  
    context = {
        'profile': profile,
        'followers': followers,
    }
    return render(request, 'social/follower_list.html', context)


@login_required
def followed_list(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    followed_users = UserProfile.objects.filter(followers=profile.user)  
    context = {
        'profile': profile,
        'followed_users': followed_users,
    }
    return render(request, 'social/followed_list.html', context)




# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# new stuff
from django.utils.timezone import now
@csrf_exempt
def mark_as_read(request, room_name):
    """
    Mark all messages in a conversation as read for the current user.
    """
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    # Get the conversation based on the room name
    conversation = get_object_or_404(Conversation, name=room_name)

    # Mark all unread messages as read for the current user in this conversation
    messages = conversation.conversation_messages.filter(
        message_status__user=request.user,
        message_status__is_read=False
    )

    for message in messages:
        message_status = MessageStatus.objects.get(message=message, user=request.user)
        message_status.is_read = True
        message_status.read_at = now()
        message_status.save()

    return JsonResponse({'status': 'success'})


@login_required
def start_conversation(request, user_id):
    receiver = get_object_or_404(User, pk=user_id)
    sender = request.user

    # Generate a conversation name using usernames
    conversation_name = f"{sender.username}_{receiver.username}"

    # Check if a conversation already exists between these two users
    conversation, created = Conversation.objects.get_or_create(
        name=conversation_name
    )

    # If the conversation is newly created, set it as private
    if created:
        conversation.type = 'private'
        conversation.save()

    # Ensure both participants are added to the conversation
    conversation.participants.add(sender, receiver)

    # Store conversation name in session and also as the current conversation
    request.session['current_conversation'] = conversation_name

    # Redirect to the conversation list or directly into the conversation room
    return redirect("conversation_list")






from .municipality_data import municipality_barangay_data 

@login_required

@login_required
def account_setup(request):
    profile = request.user.profile

    if profile.setup_complete:
        return redirect('post-list')

    if request.method == 'POST':
        if 'skip' in request.POST:
            profile.setup_complete = True
            profile.save()
            return redirect('post-list')

        form = ProfileSetupForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.setup_complete = True
            profile.save()

            # Add warnings to the context if they exist
            warnings = getattr(form, '_warning_messages', {})
            context = {
                'form': form,
                'municipality_barangay_data': municipality_barangay_data,
                'warnings': warnings,  
            }

            return redirect('post-list')

    else:
        form = ProfileSetupForm(instance=profile)

    # Add warnings to the context if they exist
    warnings = getattr(form, '_warning_messages', {})
    context = {
        'form': form,
        'municipality_barangay_data': municipality_barangay_data,
        'warnings': warnings,  #
    }

    return render(request, 'social/account_setup.html', context)




from .models import Post, Like, Comment, SharedPost, Hashtag

def get_personalized_feed(user, limit=10):
    """
    Fetches personalized posts based on user's interactions.
    It will consider posts that the user has liked, commented on, or shared.
    """
    # Get hashtags associated with posts the user has liked, commented on, or shared
    liked_posts = Like.objects.filter(user=user).values_list('post', flat=True)
    commented_posts = Comment.objects.filter(author=user).values_list('post', flat=True)
    shared_posts = SharedPost.objects.filter(shared_by=user).values_list('original_post', flat=True)

    # Get all hashtags related to posts the user has interacted with
    interacted_posts_ids = set(liked_posts) | set(commented_posts) | set(shared_posts)
    hashtags = Hashtag.objects.filter(posts__in=interacted_posts_ids).distinct()

    # Get posts related to these hashtags, ordered by their creation date
    personalized_posts = Post.objects.filter(hashtags__in=hashtags).distinct().order_by('-created_on')[:limit]
    
    return personalized_posts


import random
from .models import Post

def get_random_posts(limit=10):
    """
    Fetches random posts from the database.
    This function will simply return random posts without any user interaction filtering.
    """
    all_posts = Post.objects.all()
    random_posts = random.sample(list(all_posts), min(len(all_posts), limit))
    return random_posts




from django.contrib import messages
from .forms import FeedbackForm

def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user if request.user.is_authenticated else None
            feedback.save()
            messages.success(request, "there is a new feedback")
            return redirect('post-list') 
        else:
            print(form.errors)  
    else:
        form = FeedbackForm()
    return render(request, 'social/submit_feedback.html', {'form': form})

def recent_activity(request):
    if request.user.is_authenticated:
        feedback_entries = Feedback.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        feedback_entries = []

    formatted_feedback_dates = [
        localtime(feedback.created_at).strftime('%m/%d/%Y') for feedback in feedback_entries
    ]
    return render(request, 'social/submit_feedback.html', {'feedback_dates': formatted_feedback_dates})





from .forms import GroupRuleForm

@login_required
def create_group_rule(request, group_id):
    group = Group.objects.get(id=group_id)
    
    if request.user != group.creator and request.user not in group.admins.all():
        return redirect('group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = GroupRuleForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.group = group
            rule.save()
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupRuleForm()

    return render(request, 'social/group_rule_create.html', {'form': form, 'group': group})



from django.core.mail import send_mail
from django.core.mail import send_mail
from .models import EventReminder


class EventReminderForm(forms.ModelForm):
    class Meta:
        model = EventReminder
        fields = ['event']  

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user')  
        super().__init__(*args, **kwargs)
        if user:
            self.fields['event'].queryset = Event.objects.all()





from .task import send_event_reminder

logger = logging.getLogger(__name__)

@login_required
def set_event_reminder(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventReminderForm(request.POST)
        if form.is_valid():
            try:
                # Save the form instance
                event_reminder = form.save(commit=False)
                event_reminder.user = request.user
                event_reminder.event = event
                event_reminder.save()

                # Send confirmation email
                reminder_email = form.cleaned_data['email']
                send_confirmation_email(event_reminder, reminder_email)

                # Define reminder intervals in hours 
                reminder_hours = [24, 72, 120]  

                for hours in reminder_hours:
                    countdown_seconds = hours * 60 * 60 
                    send_event_reminder.apply_async(args=[event_reminder.id], countdown=countdown_seconds)

                messages.success(request, 'Event reminder has been set successfully!')
                return redirect('event_detail', pk=event.id)

            except Exception as e:
                logger.error(f"Error setting reminder for event {event.id}: {str(e)}")
                messages.error(request, f'Error setting reminder: {str(e)}')

    else:
        form = EventReminderForm()

    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'social/event_detail.html', context)




from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

def send_confirmation_email(event_reminder, user_email):
    # Get the event date in the user's local time zone
    event_date = timezone.localtime(event_reminder.event.date)

    # Format the event date in a readable format
    formatted_event_date = event_date.strftime("%B %d, %Y, %I:%M %p") 

    # Get the location based on the event type
    if event_reminder.event.location_type == 'inside':
        location = f"University of Antique \n"\
                   f"Department: {event_reminder.event.department}, \n" \
                   f"Building: {event_reminder.event.building}, \n" \
                   f"Room: {event_reminder.event.room_number}\n"
    elif event_reminder.event.location_type == 'outside':
        location = f"Outside the University of Antique \n"\
                   f"Province: {event_reminder.event.province},\n " \
                   f"Municipality: {event_reminder.event.municipality}, \n" \
                   f"Barangay: {event_reminder.event.barangay}, \n" \
                   f"Location: {event_reminder.event.specific_location}"
    else:
        location = "Location details not provided."

    # Prepare the email subject and message
    subject = f"Confirmation for {event_reminder.event.name}"
    message = f"Hello {event_reminder.user.username},\n\n" \
              f"You have successfully set a reminder for the event '{event_reminder.event.name}' " \
              f"scheduled on {formatted_event_date}.\n\n" \
              f"Event Location: {location}\n" \
              f"Event Description: {event_reminder.event.description}\n\n" \
              f"Thank you for using our service!"

    # Send the confirmation email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  
        [user_email], 
        fail_silently=False,
    )



