# API Endpoints Documentation

Базовый URL (redirect): `http://127.0.0.1:8000/` — корень перенаправляет на `http://127.0.0.1:8000/api/v1/movies/`.

API основной префикс: `http://127.0.0.1:8000/api/v1`

Примечание: часть стандартных Djoser/JWT маршрутов подключены отдельно под `/auth/` (без `/api/v1` префикса).

---

## Общие маршруты

- `GET /` — редирект на `/api/v1/movies/`
- `GET /auth-test/` — статическая страница для тестирования cookie flows (см. `core.views.auth_test`)
- `GET /admin/` — Django admin

---

## Users / Auth (custom, под префиксом `/api/v1/auth/`)

Все пути ниже находятся под `http://127.0.0.1:8000/api/v1/auth/`.

### Регистрация
**POST** `/api/v1/auth/register/`
- **Описание**: Регистрация нового пользователя
- **Auth**: Нет
- **Request**:
```json
{ "username": "user123", "email": "user@example.com", "password": "securepass123", "passwordConfirm": "securepass123" }
```
- **Response** (201):
```json
{ "success": true, "user": { "id": 1, "username": "user123", "email": "user@example.com", "avatarUrl": null, "isModerator": false, "createdAt": null } }
```

### Логин
**POST** `/api/v1/auth/login/`
- **Описание**: Аутентификация; возвращает JWT и данные пользователя
- **Auth**: Нет
- **Request**:
```json
{ "username": "user123", "password": "securepass123", "useCookie": false }
```
- **Response** (200):
```json
{
  "success": true,
  "user": { /* PublicUserSerializer */ },
  "tokens": { "access": "<token>", "refresh": "<token>" }
}
```
- **Примечание**: если `useCookie: true`, refresh токен устанавливается в httpOnly cookie (имена и параметры зависят от настроек `SIMPLE_JWT_REFRESH_COOKIE*`).

### Логаут
**POST** `/api/v1/auth/logout/`
- **Описание**: Попытка blacklist'ить refresh token (из cookie или из body)
- **Auth**: Нет (но полезно передавать refresh)
- **Request** (опционально): `{ "refresh": "<refresh_token>" }`
- **Response** (200): `{ "success": true }`

### Запрос на роль модератора
**POST** `/api/v1/auth/moderator-request/`
- **Описание**: Создать заявку на роль модератора
- **Auth**: Да
- **Request**: `{ "message": "..." }` (message опционально)
- **Response** (200): `{ "success": true, "request": { "id": <id>, "status": "pending", "created_at": "..." } }`

### Текущий пользователь (мой профиль)
**GET** `/api/v1/auth/me/`
- **Описание**: Возвращает данные текущего аутентифицированного пользователя
- **Auth**: Да
- **Response** (200):
```json
{ "success": true, "user": { /* PublicUserSerializer */ } }
```

---

## Djoser / JWT (под `/auth/` без `api/v1`)

Проект подключает стандартные `djoser` маршруты под префиксом `/auth/` в корневом `urls.py`:

- `POST /auth/jwt/create/` — получить JWT (djoser/simplejwt)
- `POST /auth/jwt/refresh/` — обновить access (djoser/simplejwt)
- `POST /auth/users/` и др. — стандартные djoser endpoints (зависит от конфигурации)

Эти маршруты предоставляются внешней библиотекой `djoser` и доступны одновременно с кастомными `/api/v1/auth/` путями.

---

## Movies (под `/api/v1/movies/`)

Базовый префикс: `http://127.0.0.1:8000/api/v1/movies/`

### Список фильмов
**GET** `/api/v1/movies/`
- **Описание**: Возвращает упрощённые превью одобренных фильмов
- **Auth**: Нет
- **Query params**: `page`, `search`, `genre` (id или comma list), `tags` (include/exclude with `-`), `year`, `country`, `ordering`
- **Response** (200):
```json
{
  "results": [
    { "id": 1, "title": "Blade Runner", "posterUrl": "https://...", "year": 1982, "duration": 117, "rating": 8.1, "genres": ["Sci-Fi"] }
  ],
  "next": null,
  "previous": null
}
```

### Детали фильма
**GET** `/api/v1/movies/<id>/`
- **Описание**: Полная информация о фильме и список последних top-level отзывов (по умолчанию 5)
- **Auth**: Нет
- **Query params**: `reviews_limit`
- **Response** (200): см. `MovieDetailSerializer` — включает `posterUrl`, `videoUrl`, `genres`, `tags`, `actors`, `director`, `duration` (минуты), `reviews` (массив `ReviewSerializer`)

### Пагинированные отзывы фильма
**GET** `/api/v1/movies/<id>/reviews/`
- **Описание**: Пагинированные top-level отзывы (новые первыми)
- **Auth**: Нет
- **Response**: страница отзывов (см. `ReviewsPagination` / `ReviewSerializer`)

### Создание фильма (модераторы)
**POST** `/api/v1/movies/create/`
- **Описание**: Создать новый фильм. Доступно только пользователям с ролью `moderator`.
- **Auth**: Да (Bearer или cookie)
- **Content-Type**: `multipart/form-data` (поддерживает поле `poster` для загрузки изображения)
- **Request fields**:
  - `title` (string, required)
  - `description` (string, optional)
  - `year` (int, optional)
  - `video_url` (string, optional)
  - `duration` (int, minutes, optional)
  - `poster` (file, optional) — сохраняется в `MEDIA_ROOT/posters/`
  - `actors` (array of strings) — элементы могут быть id или имя в виде `"First Last"`
  - `directors` (array of strings) — элементы могут быть id или имя
  - `country` (id or name, optional)
- **Behavior**:
  - Загруженный файл сохраняется в `MEDIA_ROOT/posters/<uuid>.<ext>` и в `poster_url` записывается `MEDIA_URL/posters/<filename>`.
  - Если актер/режиссёр передан как id — связывается существующий объект, иначе создаётся новый `Actor`/`Director` по имени (split на firstname/lastname).
  - `duration` в запросе указывается в минутах; в модели сохраняется как `DurationField`.
  - Создаётся запись `Movie`, привязываются актёры/режиссёры и страна.
- **Response** (201):
```json
{ "success": true, "movie": { /* MovieDetailSerializer */ } }
```
- **Ошибки**:
  - 400 Bad Request — некорректные/отсутствующие данные
  - 401 Unauthorized — не аутентифицирован
  - 403 Forbidden — пользователь не модератор

### Редактирование фильма (модераторы)
**PATCH** `/api/v1/movies/<id>/edit/`
- **Описание**: Частичное обновление полей фильма. Доступно только модераторам.
- **Auth**: Да
- **Content-Type**: `multipart/form-data` (для замены `poster`) или `application/json`
- **Request fields**: любые из полей создания (`title`, `description`, `year`, `video_url`, `duration`, `poster`, `actors`, `directors`, `country`, `tags`)
- **Поведение**:
  - Поля, присланные в запросе, обновляются; если `poster` передан — заменяет текущую картинку.
  - `tags` — список имён или id: существующие id будут привязаны, имена создаются автоматически.
- **Response** (200):
```json
{ "success": true, "movie": { /* MovieDetailSerializer */ } }
```
- **Ошибки**:
  - 400 Bad Request — некорректные данные
  - 401 Unauthorized — не аутентифицирован
  - 403 Forbidden — не модератор


---

## Reviews / Posts

### Создать отзыв
**POST** `/api/v1/movies/posts/create/`
- **Описание**: Создать новый отзыв (только топ‑уровнев пост)
- **Auth**: Да
- **Request**: `{ "movie": <movie_id>, "text": "..." }`
- **Response** (201): `ReviewSerializer` представление нового отзыва

### Лайк/анлайк отзыва (toggle)
**POST** `/api/v1/movies/posts/<id>/like/`
- **Описание**: Toggle like для текущего пользователя
- **Auth**: Да
- **Response** (200): `{ "id": <id>, "likes": <count>, "likedByCurrentUser": true|false }`

---

## Примеры использования (с учётом префикса `/api/v1`)

Пример запроса списка фильмов:
```javascript
fetch('/api/v1/movies/?page=1&search=cyberpunk')
  .then(r => r.json())
  .then(data => console.log(data));
```

Пример создания отзыва (Bearer):
```javascript
fetch('/api/v1/movies/posts/create/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ movie: 1, text: 'Отличный фильм!' })
})
```

Пример получения профиля текущего пользователя:
```javascript
fetch('/api/v1/auth/me/', { headers: { 'Authorization': `Bearer ${accessToken}` } })
  .then(r => r.json())
```

---

## HTTP коды ответов

- 200 OK — успешный запрос
- 201 Created — ресурс создан
- 400 Bad Request — ошибка валидации
- 401 Unauthorized — требуется авторизация
- 403 Forbidden — доступ запрещён
- 404 Not Found — ресурс не найден
- 500 Internal Server Error — ошибка сервера


3. **Пагинация**: параметры `page` (номер) и `page_size` (размер). Поле `hasMore` показывает, есть ли ещё страницы.

4. **Фильтры по жанрам и тегам**: можно передавать несколько значений:
   - Жанры: `?genre=1&genre=2` или `?genre=1,2`
   - Теги: `?tags=cyberpunk,-drama` (минус означает исключение)

5. **Сортировка**: по умолчанию по дате. Используйте `?ordering=-rating` для сортировки по рейтингу.
