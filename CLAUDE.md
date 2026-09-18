# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Django app for organizing local community events and groups (an Eventbrite/Nextdoor-style mashup): users create/RSVP to events, form groups, and post/comment/like within those groups.

## Commands

Activate the project's venv first (it lives inside this directory, not the parent):

```bash
source venv/bin/activate
```

Common commands (run from this directory, where `manage.py` lives):

```bash
python manage.py runserver
python manage.py migrate
python manage.py makemigrations <app>
python manage.py test                 # all apps
python manage.py test events           # single app
python manage.py test events.tests.SomeTestCase.test_something  # single test
python manage.py createsuperuser
```

There is no `requirements.txt` — dependencies (Django, django-environ, Pillow) are only reflected in `venv/`. If you add a dependency, install it in this venv and consider generating a requirements file.

Settings load `SECRET_KEY` and `DEBUG` from a local `.env` file (via `django-environ`) at the project root — not committed to git.

## Architecture

Four Django apps under `config` (the project package with `settings.py`/`urls.py`), each mounted at a URL prefix in `config/urls.py`:

- **`users`** — custom user model (`AUTH_USER_MODEL = 'users.CustomUser'`), signup/login/profile/password-reset views.
- **`events`** — `Event` and `RSVP` models.
- **`groups`** — `Group` and `GroupMembership` models.
- **`posts`** — `Post`, `Comment` (self-referential for threaded replies), and a generic `Like` model.

All models use UUID primary keys (`models.UUIDField(default=uuid.uuid4)`) instead of auto-incrementing IDs — this was a deliberate fix for sequential-ID scraping, per the comment in `users/models.py`. Keep this pattern for any new model.

### Cross-app relationships

`events.Event.group` and `posts.Post.group` both FK into `groups.Group`, and `posts` imports `groups.models` directly for membership checks — `groups` is the hub app that `events` and `posts` depend on. There's no reverse dependency, so avoid introducing one (e.g. `groups` should not import from `posts` or `events`).

### Permission model (reimplemented per view, not via a shared decorator/mixin)

Every app hand-rolls its own visibility/authorization checks in the view functions rather than using Django permissions or a shared helper — when adding a new view, follow the existing pattern in that app's `views.py` rather than introducing a new mechanism:

- **Groups** (`groups/views.py`): `is_group_admin(user, group)` checks for an `APPROVED` membership with `role=ADMIN`. Membership `status` (`approved`/`pending`/`banned`) gates joining; `role` (`member`/`moderator`/`admin`) gates moderation actions (approve, promote, ban/unban). Group-level booleans (`is_public`, `is_discoverable`, `posts_visible_to_non_members`, `member_list_public`) independently control discovery, post visibility, and member-list visibility — these are combined per-view (see `group_detail`, `can_view_posts` vs `can_interact_posts`), not derived from a single "privacy level".
- **Posts** (`posts/views.py`): `get_membership(user, group)` returns an approved `GroupMembership` or `None`; `can_view`/`can_interact` are recomputed in `post_list`, `post_detail`, `post_create`, `comment_create`, and `toggle_like` individually rather than shared — when changing the visibility rules, update all of these call sites.
- **Likes** (`posts/models.Like`): generic via `ContentType`/`object_id`, currently used for both `Post` and `Comment` (see `model_map` in `posts.views.toggle_like`). `unique_together = ('user', 'content_type', 'object_id')` enforces one like per user per object.
- **Events** (`events/views.py`): `Event.visibility` (`public`/`unlisted`/`private`) controls listing in `event_list` (only `PUBLIC` events are queried); `address_visible_to_all` vs. requiring a `GOING` RSVP controls whether `exact_address` is shown in `event_detail`. Edit/delete are restricted to `event.organizer == request.user` via direct `HttpResponseForbidden` checks (no decorator).

### Templates & static files

`templates/base.html` is the shared base; each app also has its own `templates/<app>/` directory (Django's `APP_DIRS` template loading). Global static assets live in `static/css/`; user-uploaded media (profile pictures, group images, post images) goes to `media/`, split into `profiles/`, `groups/`, and `posts/` subdirectories per `upload_to` on the relevant `ImageField`.

## Testing

`tests.py` in each app is currently just Django boilerplate with no real test cases — there is no existing test suite or pattern to follow yet.
