from .views import get_conversations


def chat_panel(request):
    if not request.user.is_authenticated:
        return {}

    conversations = get_conversations(request.user)
    unread_count = sum(c['unread_count'] for c in conversations)

    return {
        'chat_conversations': conversations[:8],
        'chat_unread_count': unread_count,
    }
