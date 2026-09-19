from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Message

User = get_user_model()


def get_conversations(user):
    sent_to = Message.objects.filter(sender=user).values_list('recipient_id', flat=True)
    received_from = Message.objects.filter(recipient=user).values_list('sender_id', flat=True)
    partner_ids = set(sent_to) | set(received_from)

    conversations = []
    for partner in User.objects.filter(id__in=partner_ids):
        last_message = Message.objects.filter(
            Q(sender=user, recipient=partner) | Q(sender=partner, recipient=user)
        ).order_by('-created_at').first()
        unread_count = Message.objects.filter(sender=partner, recipient=user, is_read=False).count()
        conversations.append({
            'partner': partner,
            'last_message': last_message,
            'unread_count': unread_count,
        })

    conversations.sort(key=lambda c: c['last_message'].created_at, reverse=True)
    return conversations


@login_required
def conversation_list(request):
    conversations = get_conversations(request.user)
    return render(request, 'chat/conversation_list.html', {'conversations': conversations})


@login_required
def start_conversation(request):
    username = request.GET.get('username', '').strip()
    partner = User.objects.filter(username__iexact=username).exclude(id=request.user.id).first()

    if partner:
        return redirect('conversation_detail', user_id=partner.id)

    if username:
        django_messages.error(request, f'No user found with username "{username}".')

    return redirect('conversation_list')


@login_required
def conversation_detail(request, user_id):
    partner = get_object_or_404(User, id=user_id)
    if partner == request.user:
        return HttpResponseForbidden("You can't message yourself.")

    messages_list = Message.objects.filter(
        Q(sender=request.user, recipient=partner) | Q(sender=partner, recipient=request.user)
    )
    Message.objects.filter(sender=partner, recipient=request.user, is_read=False).update(is_read=True)

    return render(request, 'chat/conversation_detail.html', {
        'partner': partner,
        'messages_list': messages_list,
    })


@login_required
def send_message(request, user_id):
    partner = get_object_or_404(User, id=user_id)

    if partner != request.user and request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(sender=request.user, recipient=partner, body=body)

    return redirect('conversation_detail', user_id=partner.id)
