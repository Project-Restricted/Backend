# Authentication (Djoser + SimpleJWT)

Краткое руководство для фронтенда (React + TypeScript) по работе с авторизацией, которую подключили через `djoser` и `djangorestframework-simplejwt`.

Базовые endpoints (в проекте подключены под префиксом `/auth/`):
- `POST /auth/users/` — регистрация пользователя (создаёт запись, по умолчанию без активации).
- `POST /auth/jwt/create/` — логин (возвращает `{ access, refresh }`).
- `POST /auth/jwt/refresh/` — обновление access (отправить `{ refresh }`).
- `POST /auth/jwt/blacklist/` — аннулировать refresh (logout при использовании blacklist).
- `GET /auth/users/me/` — получить профиль текущего пользователя (требует авторизации).

Пример: регистрация (fetch)
```ts
// src/api/auth.ts
type RegisterPayload = { email: string; username: string; password: string; re_password: string };
async function register(data: RegisterPayload) {
  const res = await fetch('/auth/users/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Registration failed');
  return res.json();
}
```

Пример: логин (получение токенов)
```ts
type TokenResponse = { access: string; refresh: string };
async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch('/auth/jwt/create/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error('Login failed');
  return res.json();
}
```

Куда сохранять токены (простой подход для обучения)
- `access`: хранить в памяти (React state / context). Это безопаснее против XSS, но теряется при reload.
- `refresh`: можно хранить в `localStorage` для простоты. Для боевого проекта рекомендую хранить `refresh` в `httpOnly` cookie.

Использование токена для запросов
```ts
async function apiGet(path: string, accessToken: string) {
  const res = await fetch(path, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}
```

Обновление access с использованием refresh
```ts
async function refreshAccess(refreshToken: string) {
  const res = await fetch('/auth/jwt/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken }),
  });
  if (!res.ok) throw new Error('Refresh failed');
  return res.json(); // { access }
}
```

Logout (аннулирование refresh)
```ts
async function logout(refreshToken: string) {
  await fetch('/auth/jwt/blacklist/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken }),
  });
  // очистить локальное состояние/хранилище
}
```

Замечания и рекомендации
- В режиме разработки письма для активации/сброса пароля будут выводиться в консоль (EMAIL_BACKEND настроен на console backend).
- Если хотите логиниться по `username` вместо `email`, измените `LOGIN_FIELD` в `DJOSER` или используйте соответствующие поля при запросе.
- Для продакшна: используйте `https`, `Secure`/`HttpOnly` флаги для cookie, ограничьте CORS и перенесите секреты в окружение.

Если нужно, могу добавить пример React hook (useAuth) и контекст для хранения access/refresh и автоматического refresh-логики.

