from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from groups.models import Group, GroupMembership
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

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'group': group,
        'can_interact': can_interact,
    })