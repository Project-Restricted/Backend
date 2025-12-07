# Copilot / AI agent instructions for this repository

Preferred model: **Enable GPT-5 mini for all clients**. Use GPT-5 mini where a model choice is available.

**Project Overview:**
- Django 5.x REST API project. Main apps: `users`, `movies`, `core`.
- Database: SQLite at `cinemaportal/db.sqlite3` (development). Media in `media/` (posters under `media/posters`).
- Auth: custom user model `users.User` (see `users/models.py`).
- CORS is enabled project-wide and a custom middleware `core.middleware.CustomCorsMiddleware` is used (see `cinemaportal/settings.py`).

**Where to look first:**
- Global settings: `cinemaportal/settings.py` (DEBUG=True, CORS, REST_FRAMEWORK defaults).
- CLI entry: `cinemaportal/manage.py` (standard Django management).
- Models: `movies/models/*.py` (one model per file: `movie.py`, `actor.py`, etc.).
- Serializers: `movies/serializers/*` (`movie_serializer.py`, `movie_detail.py`) — follow existing field naming (e.g. `posterUrl` mapping to `poster_url`).
- Views: `movies/views/*` (`movie_views.py`, `movie_detail.py`) — DRF generic views are used with query-parameter filtering.
- Pagination helper: `movies/pagination.py` (project uses `InfiniteScrollPagination`).

**API / Code patterns to follow (concrete examples):**
- Use DRF generics (see `MovieListView` in `movies/views/movie_views.py`).
- Queryset performance: use `select_related('country')` + `prefetch_related('genres', 'actors', 'tags')` as in `MovieListView.get_queryset()`.
- Query parameter parsing conventions:
  - `search` performs multi-field icontains across title / tags / actors.
  - `genre` accepts comma-separated ids or repeated query params; parse both forms.
  - `tags` supports include/exclude tokens (exclude tokens start with `-`).
  - `ordering` is whitelisted (example allowed values: `rating`, `-rating`, `year`, `-year`, `id`, `-id`).
- Serializer conventions: return `duration` in minutes using a `SerializerMethodField` (see `MovieListSerializer.get_duration`), and expose `posterUrl` as `source='poster_url'`.

**Developer workflow (Windows / PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python cinemaportal\manage.py migrate
python cinemaportal\manage.py runserver
python cinemaportal\manage.py test
```

Notes:
- Don't assume a production DB; migrations live in each app under `*/migrations/`.
- Tests live in each app's `tests.py` (run via `manage.py test`).

**Conventions & tips for edits:**
- Keep one model per file in `movies/models/` and follow existing naming (snake_case fields, camelCase output via serializer fields when necessary).
- When adding an endpoint:
  1. Add/extend a serializer in `movies/serializers/`.
  2. Add a view (prefer DRF generics) in `movies/views/` and reuse `movies/pagination.py` if appropriate.
  3. Register the view in `movies/urls.py` and ensure `cinemaportal/urls.py` includes the `movies` router/urls.
- Preserve `approved=True` filter on movie lists unless intentionally changing visibility rules.

**Safety / environment notes:**
- `SECRET_KEY` is present in `cinemaportal/settings.py` for development. Do not commit different secrets here without coordinating with maintainers.
- `DEBUG=True` is set; avoid assuming production settings.

If anything is unclear or you want additional examples (routing, a full example endpoint, or test guidance), ask and I'll expand this file.
