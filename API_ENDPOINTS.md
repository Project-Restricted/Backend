# API Endpoints Documentation

Базовый URL: `http://127.0.0.1:8000/api/v1`

## Авторизация (Auth)

### Регистрация
**POST** `/auth/register/`
- **Описание**: Регистрация нового пользователя
- **Требует Auth**: Нет
- **Request Body**:
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepass123"
}
```
- **Response** (201 Created):
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "role": "user"
}
```

### Логин (получить токены)
**POST** `/auth/login/`
- **Описание**: Получить access и refresh токены
- **Требует Auth**: Нет
- **Request Body**:
```json
{
  "username": "user123",
  "password": "securepass123",
  "useCookie": false
}
```
- **Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```
- **Примечание**: Если `useCookie: true`, refresh token будет установлен в httpOnly cookie

### Логаут
**POST** `/auth/logout/`
- **Описание**: Выход из системы (blacklist refresh token)
- **Требует Auth**: Нет (или access token)
- **Request Body** (опционально):
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```
- **Response** (200 OK):
```json
{
  "detail": "Успешно вышли из системы"
}
```

### Запрос на роль модератора
**POST** `/auth/moderator-request/`
- **Описание**: Подать заявку на роль модератора
- **Требует Auth**: Да (Bearer token или cookie)
- **Request Body**:
```json
{
  "message": "Я хочу стать модератором, потому что..."
}
```
- **Response** (201 Created):
```json
{
  "id": 5,
  "user": 1,
  "message": "Я хочу стать модератором...",
  "status": "pending",
  "created_at": "2025-12-03T12:30:00Z"
}
```

---

## Фильмы (Movies)

### Список фильмов (с фильтрацией и пагинацией)
**GET** `/movies/`
- **Описание**: Получить список одобренных фильмов
- **Требует Auth**: Нет
- **Query Parameters**:
  - `page` (int): номер страницы (по умолчанию 1)
  - `page_size` (int): размер страницы (по умолчанию 20)
  - `search` (str): поиск по названию, тегам, актёрам
  - `genre` (int or comma-separated): ID жанра(ов)
  - `tags` (str): фильтр по тегам (поддерживает префикс `-` для исключения)
  - `year` (int): год выпуска
  - `country` (int or str): страна по ID или названию
  - `ordering` (str): сортировка (`rating`, `-rating`, `year`, `-year`, `id`, `-id`)

- **Response** (200 OK):
```json
{
  "films": [
    {
      "id": 1,
      "title": "Blade Runner",
      "posterUrl": "https://...",
      "year": 1982,
      "rating": 8.1,
      "duration": 117,
      "genres": ["Sci-Fi", "Thriller"],
      "tags": ["cyberpunk", "dystopia"],
      "country": "USA",
      "actors": ["Harrison Ford", "Rutger Hauer"]
    }
  ],
  "hasMore": true
}
```

### Детали фильма (с отзывами)
**GET** `/movies/<id>/`
- **Описание**: Получить полную информацию о фильме + последние отзывы
- **Требует Auth**: Нет
- **Query Parameters**:
  - `reviews_limit` (int): количество отзывов (по умолчанию 5)

- **Response** (200 OK):
```json
{
  "id": 1,
  "title": "Blade Runner",
  "posterUrl": "https://...",
  "videoUrl": "https://...",
  "year": 1982,
  "rating": 8.1,
  "duration": 117,
  "description": "A blade runner must pursue and terminate...",
  "genres": ["Sci-Fi", "Thriller"],
  "tags": ["cyberpunk", "dystopia"],
  "country": "USA",
  "actors": ["Harrison Ford", "Rutger Hauer"],
  "director": "Ridley Scott",
  "reviews": [
    {
      "id": 42,
      "text": "Отличный фильм!",
      "createdAt": 1701619200,
      "likes": 3,
      "likedByCurrentUser": false,
      "user": {
        "id": 5,
        "username": "ivan",
        "avatarUrl": "https://..."
      }
    }
  ]
}
```

### Пагинированные отзывы на фильм
**GET** `/movies/<id>/reviews/`
- **Описание**: Получить страницу отзывов на фильм (новые первыми)
- **Требует Auth**: Нет
- **Query Parameters**:
  - `page` (int): номер страницы (по умолчанию 1)
  - `page_size` (int): размер страницы (по умолчанию 5)

- **Response** (200 OK):
```json
{
  "reviews": [
    {
      "id": 42,
      "text": "Отличный фильм!",
      "createdAt": 1701619200,
      "likes": 3,
      "likedByCurrentUser": false,
      "user": {
        "id": 5,
        "username": "ivan",
        "avatarUrl": "https://..."
      }
    }
  ],
  "hasMore": true
}
```

---

## Отзывы (Reviews/Posts)

### Создание отзыва
**POST** `/movies/posts/create/`
- **Описание**: Создать новый отзыв на фильм
- **Требует Auth**: Да (Bearer token или cookie)
- **Request Body**:
```json
{
  "movie": 1,
  "text": "Это отличный фильм, мне очень понравился!"
}
```
- **Response** (201 Created):
```json
{
  "id": 43,
  "text": "Это отличный фильм, мне очень понравился!",
  "createdAt": 1701619260,
  "likes": 0,
  "likedByCurrentUser": false,
  "user": {
    "id": 5,
    "username": "ivan",
    "avatarUrl": "https://..."
  }
}
```
- **Ошибки**:
  - 400 Bad Request: неверные данные (отсутствует `movie` или `text`)
  - 401 Unauthorized: не авторизован
  - 404 Not Found: фильм не найден

### Лайк/Анлайк отзыва (toggle)
**POST** `/movies/posts/<id>/like/`
- **Описание**: Поставить или снять лайк на отзыв
- **Требует Auth**: Да (Bearer token или cookie)
- **Request Body**: пусто или `{}`

- **Response** (200 OK):
```json
{
  "id": 42,
  "likes": 4,
  "likedByCurrentUser": true
}
```
- **Ошибки**:
  - 401 Unauthorized: не авторизован
  - 404 Not Found: отзыв не найден

---

## Как использовать авторизацию

### JWT Token (Bearer)
Все защищённые эндпоинты принимают заголовок:
```
Authorization: Bearer <access_token>
```

Пример:
```javascript
fetch('/api/v1/movies/posts/create/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    movie: 1,
    text: "Отличный фильм!"
  })
})
```

### Cookie-based (httpOnly refresh)
Если при логине передать `useCookie: true`, refresh token будет установлен в cookie:
```javascript
fetch('/api/v1/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    username: 'user123',
    password: 'pass123',
    useCookie: true
  })
})
  .then(r => r.json())
  .then(data => {
    // access token в ответе, refresh в cookie
    localStorage.setItem('access', data.access);
  })
```

Тогда для защищённых запросов:
```javascript
fetch('/api/v1/movies/posts/create/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  credentials: 'include', // отправить cookie
  body: JSON.stringify({ movie: 1, text: "Отзыв" })
})
```

---

## Коды ответов

- **200 OK**: успешный запрос
- **201 Created**: ресурс успешно создан
- **400 Bad Request**: ошибка валидации данных
- **401 Unauthorized**: требуется авторизация
- **403 Forbidden**: доступ запрещён (недостаточно прав)
- **404 Not Found**: ресурс не найден
- **429 Too Many Requests**: превышен лимит запросов (rate limit)
- **500 Internal Server Error**: ошибка сервера

---

## Примеры использования (JavaScript/Fetch)

### 1. Регистрация
```javascript
async function register(username, email, password) {
  const res = await fetch('/api/v1/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  return res.json();
}
```

### 2. Логин
```javascript
async function login(username, password) {
  const res = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, useCookie: false })
  });
  const data = await res.json();
  localStorage.setItem('access', data.access);
  localStorage.setItem('refresh', data.refresh);
  return data;
}
```

### 3. Получить список фильмов
```javascript
async function getMovies(page = 1, search = '') {
  const params = new URLSearchParams({ page, search });
  const res = await fetch(`/api/v1/movies/?${params}`);
  return res.json();
}
```

### 4. Создать отзыв
```javascript
async function createReview(movieId, text, accessToken) {
  const res = await fetch('/api/v1/movies/posts/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ movie: movieId, text })
  });
  if (!res.ok) throw new Error('Failed to create review');
  return res.json();
}
```

### 5. Лайкнуть отзыв
```javascript
async function toggleLike(postId, accessToken) {
  const res = await fetch(`/api/v1/movies/posts/${postId}/like/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  if (!res.ok) throw new Error('Failed to toggle like');
  return res.json(); // { id, likes, likedByCurrentUser }
}
```

---

## Примечания для фронтенда

1. **Дата в Unix timestamp**: поле `createdAt` — это Unix timestamp (целое число). Преобразуйте в дату так:
   ```javascript
   const date = new Date(createdAt * 1000);
   ```

2. **Поле `likedByCurrentUser`**: использует информацию о текущем пользователе из токена. Если не авторизован — всегда `false`.

3. **Пагинация**: параметры `page` (номер) и `page_size` (размер). Поле `hasMore` показывает, есть ли ещё страницы.

4. **Фильтры по жанрам и тегам**: можно передавать несколько значений:
   - Жанры: `?genre=1&genre=2` или `?genre=1,2`
   - Теги: `?tags=cyberpunk,-drama` (минус означает исключение)

5. **Сортировка**: по умолчанию по дате. Используйте `?ordering=-rating` для сортировки по рейтингу.
