# API Contract

## Общая информация
- **Base URL:** `https://api.cinemaportal.com/api/v1/`
- **Format:** JSON
- **Auth:** JWT (в заголовке `Authorization: Bearer <token>`)

---

## Разделы API

### 1. Auth
- `POST /auth/register/` — регистрация пользователя
- `POST /auth/login/` — вход в систему
- `GET /auth/profile/` — получить информацию о текущем пользователе

---
https://api.cinemaportal.com/api/v1/GET /movies/{id}/
### 2. Movies
- `GET /movies/` — список фильмов
- `GET /movies/{id}/` — информация о фильме
- `POST /movies/` — добавить фильм *(admin only)*
- `PUT /movies/{id}/` — обновить фильм *(admin only)*
- `DELETE /movies/{id}/` — удалить фильм *(admin only)*

---

### 3. Actors
- `GET /actors/` — список актёров
- `GET /actors/{id}/` — информация об актёре

---

### 4. Reviews
- `GET /movies/{id}/reviews/` — получить отзывы фильма
- `POST /movies/{id}/reviews/` — добавить отзыв *(только авторизованный пользователь)*
- `DELETE /reviews/{id}/` — удалить свой отзыв

---

### 5. Users
- `GET /users/{id}/` — профиль пользователя *(admin only)*

---

## Примеры ответов и ошибок
(повторяются по шаблону, как мы уже делали для /movies/{id}/)
