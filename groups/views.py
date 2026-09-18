from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Group, GroupMembership
from .forms import GroupForm



def group_list(request):
    groups = Group.objects.filter(is_discoverable=True)

    search = request.GET.get('search')
    if search:
        groups = groups.filter(name__icontains=search)

    user_membership_map = {}
    if request.user.is_authenticated:
        memberships = GroupMembership.objects.filter(user=request.user, group__in=groups)
        user_membership_map = {m.group_id: m.status for m in memberships}

    group_data = [
        {'group': g, 'membership_status': user_membership_map.get(g.id)}
        for g in groups
    ]

    return render(request, 'groups/group_list.html', {
        'group_data': group_data,
        'search_query': search,
    })
def format_count(n):
    if n < 1000:
        return str(n)
    elif n < 1_000_000:
        value = n / 1000
    else:
        value = n / 1_000_000

    suffix = 'k' if n < 1_000_000 else 'M'

    if value == int(value):
        return f"{int(value)}{suffix}"
    return f"{value:.1f}{suffix}"

from posts.models import Post

def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = None
    if request.user.is_authenticated:
        membership = GroupMembership.objects.filter(group=group, user=request.user).first()

    is_admin = is_group_admin(request.user, group)
    is_member = membership is not None and membership.status == 'approved'

    approved_members = group.memberships.filter(status=GroupMembership.Status.APPROVED)
    member_count = approved_members.count()
    member_count_display = format_count(member_count)

    can_view_members = group.member_list_public or is_member
    members = approved_members if can_view_members else GroupMembership.objects.none()

    can_view_posts = group.is_public or group.posts_visible_to_non_members or is_member
    posts = group.posts.all() if can_view_posts else Post.objects.none()
    can_interact_posts = group.is_public or is_member

    pending_requests = group.memberships.filter(status=GroupMembership.Status.PENDING) if is_admin else None
    banned_members = group.memberships.filter(status=GroupMembership.Status.BANNED) if is_admin else None

    return render(request, 'groups/group_detail.html', {
        'group': group,
        'membership': membership,
        'members': members,
        'member_count': member_count,
        'member_count_display': member_count_display,
        'can_view_members': can_view_members,
        'posts': posts,
        'can_view_posts': can_view_posts,
        'can_interact_posts': can_interact_posts,
        'pending_requests': pending_requests,
        'banned_members': banned_members,
        'is_admin': is_admin,
    })


@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            GroupMembership.objects.create(group=group, user=request.user, role=GroupMembership.Role.ADMIN)
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupForm()

    return render(request, 'groups/group_form.html', {'form': form})


@login_required
def group_join(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    existing = GroupMembership.objects.filter(group=group, user=request.user).first()

    if existing and existing.status == GroupMembership.Status.BANNED:
        return HttpResponseForbidden("You have been banned from this group.")

    if not existing:
        status = GroupMembership.Status.APPROVED if group.is_public else GroupMembership.Status.PENDING
        GroupMembership.objects.create(group=group, user=request.user, status=status)

    return redirect('group_detail', group_id=group.id)


@login_required
def group_leave(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    GroupMembership.objects.filter(group=group, user=request.user).delete()
    return redirect('group_detail', group_id=group.id)


@login_required
def approve_member(request, group_id, membership_id):
    group = get_object_or_404(Group, id=group_id)
    requester_membership = GroupMembership.objects.filter(group=group, user=request.user).first()

    if not requester_membership or requester_membership.role not in [GroupMembership.Role.ADMIN, GroupMembership.Role.MODERATOR]:
        return HttpResponseForbidden("You don't have permission to approve members.")

    membership = get_object_or_404(GroupMembership, id=membership_id, group=group)
    membership.status = GroupMembership.Status.APPROVED
    membership.save()

    return redirect('group_detail', group_id=group.id)

def is_group_admin(user, group):
    if not user.is_authenticated:
        return False
    membership = GroupMembership.objects.filter(group=group, user=user, status='approved').first()
    return membership is not None and membership.role == GroupMembership.Role.ADMIN


@login_required
def group_edit(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if not is_group_admin(request.user, group):
        return HttpResponseForbidden("Only admins can edit this group.")

    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupForm(instance=group)

    return render(request, 'groups/group_form.html', {'form': form, 'editing': True})


@login_required
def promote_admin(request, group_id, membership_id):
    group = get_object_or_404(Group, id=group_id)

    if not is_group_admin(request.user, group):
        return HttpResponseForbidden("Only admins can promote members.")

    membership = get_object_or_404(GroupMembership, id=membership_id, group=group)
    membership.role = GroupMembership.Role.ADMIN
    membership.save()

    return redirect('group_detail', group_id=group.id)


@login_required
def ban_member(request, group_id, membership_id):
    group = get_object_or_404(Group, id=group_id)

    if not is_group_admin(request.user, group):
        return HttpResponseForbidden("Only admins can ban members.")

    membership = get_object_or_404(GroupMembership, id=membership_id, group=group)
    membership.status = GroupMembership.Status.BANNED
    membership.save()

    return redirect('group_detail', group_id=group.id)


@login_required
def unban_member(request, group_id, membership_id):
    group = get_object_or_404(Group, id=group_id)

    if not is_group_admin(request.user, group):
        return HttpResponseForbidden("Only admins can unban members.")

    membership = get_object_or_404(GroupMembership, id=membership_id, group=group)
    membership.status = GroupMembership.Status.APPROVED
    membership.save()

    return redirect('group_detail', group_id=group.id)
# Create your views here.
