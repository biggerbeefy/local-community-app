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


def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = None
    if request.user.is_authenticated:
        membership = GroupMembership.objects.filter(group=group, user=request.user).first()

    members = group.memberships.filter(status=GroupMembership.Status.APPROVED)
    pending_requests = None
    if membership and membership.role in [GroupMembership.Role.ADMIN, GroupMembership.Role.MODERATOR]:
        pending_requests = group.memberships.filter(status=GroupMembership.Status.PENDING)

    return render(request, 'groups/group_detail.html', {
        'group': group,
        'membership': membership,
        'members': members,
        'pending_requests': pending_requests,
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
# Create your views here.
