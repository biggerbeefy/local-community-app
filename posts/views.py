from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from groups.models import Group, GroupMembership
from notifications.models import Notification
from .models import Post
from .forms import PostForm


def get_membership(user, group):
    if not user.is_authenticated:
        return None
    return GroupMembership.objects.filter(group=group, user=user, status='approved').first()


def post_list(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = get_membership(request.user, group)
    is_member = membership is not None

    can_view = group.is_public or group.posts_visible_to_non_members or is_member
    if not can_view:
        return HttpResponseForbidden("This group's posts are private to members.")

    can_interact = group.is_public or is_member

    posts = group.posts.all()

    return render(request, 'posts/post_list.html', {
        'group': group,
        'posts': posts,
        'can_interact': can_interact,
    })


@login_required
def post_create(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = get_membership(request.user, group)

    can_interact = group.is_public or membership is not None
    if not can_interact:
        return HttpResponseForbidden("You must be a member of this group to post.")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.group = group
            post.author = request.user
            post.save()
            return redirect('post_list', group_id=group.id)
    else:
        form = PostForm()

    return render(request, 'posts/post_form.html', {'form': form, 'group': group})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    group = post.group
    membership = get_membership(request.user, group)
    is_member = membership is not None

    can_view = group.is_public or group.posts_visible_to_non_members or is_member
    if not can_view:
        return HttpResponseForbidden("This post is private to group members.")

    can_interact = group.is_public or is_member

    top_level_comments = post.comments.filter(parent=None)

    post_content_type = ContentType.objects.get_for_model(Post)
    like_count = Like.objects.filter(content_type=post_content_type, object_id=post.id).count()
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = Like.objects.filter(
            content_type=post_content_type, object_id=post.id, user=request.user
        ).exists()

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'group': group,
        'can_interact': can_interact,
        'comments': top_level_comments,
        'comment_form': CommentForm(),
        'like_count': like_count,
        'user_has_liked': user_has_liked,
    })

from django.contrib.contenttypes.models import ContentType
from .models import Post, Comment, Like
from .forms import PostForm, CommentForm


@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    group = post.group
    membership = get_membership(request.user, group)

    can_interact = group.is_public or membership is not None
    if not can_interact:
        return HttpResponseForbidden("You must be a member of this group to comment.")

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)
            comment.save()

            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    notif_type=Notification.Type.POST_COMMENT,
                    message=f'{request.user.username} commented on your post "{post.title or "Untitled post"}"',
                    link=f'/posts/{post.id}/',
                )

    return redirect('post_detail', post_id=post.id)


@login_required
def toggle_like(request, model_name, object_id):
    model_map = {'post': Post, 'comment': Comment}
    model = model_map.get(model_name)
    if not model:
        return HttpResponseForbidden("Invalid like target.")

    obj = get_object_or_404(model, id=object_id)
    group = obj.group if model_name == 'post' else obj.post.group
    membership = get_membership(request.user, group)

    can_interact = group.is_public or membership is not None
    if not can_interact:
        return HttpResponseForbidden("You must be a member of this group to like posts.")

    content_type = ContentType.objects.get_for_model(model)
    existing = Like.objects.filter(user=request.user, content_type=content_type, object_id=object_id).first()

    if existing:
        existing.delete()
    else:
        Like.objects.create(user=request.user, content_type=content_type, object_id=object_id)

        if model_name == 'post':
            like_count = Like.objects.filter(content_type=content_type, object_id=object_id).count()
            if like_count == 10 and obj.author != request.user:
                Notification.objects.create(
                    recipient=obj.author,
                    notif_type=Notification.Type.POST_LIKES,
                    message=f'Your post "{obj.title or "Untitled post"}" reached 10 likes!',
                    link=f'/posts/{obj.id}/',
                )

    return redirect(request.META.get('HTTP_REFERER', 'post_list'))