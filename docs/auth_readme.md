# 🔐 Полное руководство по авторизации для фронтендера

**Кому:** React разработчик на TypeScript + Vite + MUI
**Что:** как регистрировать, логинить, логаутить пользователей и просить роль модератора

---

## Оглавление
1. [Что нужно знать](#что-нужно-знать)
2. [Endpoints (адреса API)](#endpoints-адреса-api)
3. [Формы и типы данных](#формы-и-типы-данных)
4. [Примеры кода — React + TS](#примеры-кода--react--ts)
5. [Как работают токены](#как-работают-токены)
6. [Cookie vs LocalStorage](#cookie-vs-localstorage)
7. [Частые ошибки и как их исправить](#частые-ошибки-и-как-их-исправить)

---

## Что нужно знать

### Как вообще это работает (в 2 минуты)

1. **Регистрация** — пользователь заполняет форму (имя, email, пароль) → отправляем на сервер → создаётся аккаунт.
2. **Логин** — пользователь вводит username/email и пароль → сервер проверяет → даёт 2 токена (access и refresh).
3. **Access токен** — это пропуск, который нужно показывать для каждого защищённого запроса (например, POST редактировать профиль).
4. **Refresh токен** — это билет для получения нового access токена, когда старый истёк (живёт дольше).
5. **Logout** — пользователь нажимает «выйти» → отправляем refresh токен на сервер → сервер его «блокирует» → пользователь удаляет токены локально.

### Главное правило

> Каждый защищённый запрос (кроме регистрации и логина) должен включать заголовок:
> ```
> Authorization: Bearer <ACCESS_TOKEN>
> ```

---

## Endpoints (адреса API)

Все endpoints находятся на **http://127.0.0.1:8000** (в разработке).

### 📝 Регистрация

**URL:** `POST /api/v1/auth/register/`

**Что отправляете (body):**
```ts
{
  username: "ivan",                    // Придуманный никнейм (уникальный)
  email: "ivan@example.com",          // Email (уникальный)
  password: "pass1234",               // Пароль
  passwordConfirm: "pass1234",        // Повтор пароля (должны совпадать)
  name: "Ivan",                       // Имя (опционально)
  lastName: "Ivanov",                 // Фамилия (опционально)
  // Поля ниже игнорируются (нет в БД):
  middleName: "Petrovich",            // Отчество (не сохраняется пока)
  birthDate: "1990-01-01"             // День рождения (не сохраняется пока)
}
```

**Что получите в ответе (успех):**
```ts
{
  success: true,
  user: {
    id: 1,
    email: "ivan@example.com",
    username: "ivan",
    avatarUrl: null,                  // URL аватарки (если поставил)
    averageRating: 0.0,               // Средняя оценка отзывов (пока всегда 0)
    reviewsCount: 0,                  // Количество написанных отзывов
    isModerator: false,               // Является ли модератором
    createdAt: 1701622800            // Время создания (Unix timestamp)
  }
}
```

**Если ошибка:**
```ts
{
  success: false,
  error: "username and email are required"  // или другая ошибка
}
```

---

### 🔑 Логин

**URL:** `POST /api/v1/auth/login/`

**Что отправляете:**
```ts
{
  username: "ivan",      // или может быть email: "ivan@example.com" (оба работают!)
  password: "pass1234",
  useCookie: false       // опционально: true если хотите refresh в httpOnly cookie
}
```

**Что получите (успех):**
```ts
{
  success: true,
  user: {
    // тот же объект User как при регистрации
  },
  tokens: {
    access: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",   // Основной токен (15 минут)
    refresh: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."   // Токен для обновления (1 день)
  }
}
```

**Если ошибка:**
```ts
{
  success: false,
  error: "Invalid credentials"
}
```

---

### 🚪 Logout (Выход)

**URL:** `POST /api/v1/auth/logout/`

**Что отправляете (вариант 1 — с refresh токеном в теле):**
```ts
{
  refresh: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Заголовки:**
```ts
{
  'Content-Type': 'application/json',
  'Authorization': 'Bearer <ACCESS_TOKEN>'  // можно любой, даже истёкший
}
```

**Что получите:**
```ts
{
  success: true
}
```

**Вариант 2 — с cookie (если при логине выбрали useCookie: true):**
Тогда refresh лежит в cookie, и можно отправить пустой POST:
```ts
fetch('/api/v1/auth/logout/', {
  method: 'POST',
  credentials: 'include'  // браузер сам добавит cookie
})
```

---

### ⭐ Заявка на модератора

**URL:** `POST /api/v1/auth/moderator-request/`

**Что отправляете:**
```ts
{
  message: "Я хочу быть модератором, потому что..."  // опционально
}
```

**Заголовки:**
```ts
{
  'Content-Type': 'application/json',
  'Authorization': 'Bearer <ACCESS_TOKEN>'  // обязательно!
}
```

**Что получите:**
```ts
{
  success: true,
  request: {
    id: 1,
    status: "pending",           // На рассмотрении (админ потом одобрит или отклонит)
    created_at: "2025-12-03T18:05:00Z"
  }
}
```

**Если уже есть заявка со статусом pending:**
```ts
{
  success: false,
  error: "You already have a pending moderator request"
}
```

---

## Формы и типы данных

### TypeScript типы (скопируйте себе в проект)

```ts
// ========== Регистрация ==========
export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  passwordConfirm: string;
  name?: string;
  lastName?: string;
  middleName?: string;      // Не сохраняется
  birthDate?: string;       // Не сохраняется
}

export interface RegisterResponse {
  success: boolean;
  user?: User;
  error?: string;
}

// ========== Логин ==========
export interface LoginPayload {
  username: string;          // или email
  password: string;
  useCookie?: boolean;
}

export interface LoginResponse {
  success: boolean;
  user?: User;
  tokens?: {
    access: string;
    refresh: string;
  };
  error?: string;
}

// ========== Пользователь ==========
export interface User {
  id: number;
  email: string;
  username: string;
  avatarUrl: string | null;
  averageRating: number;
  reviewsCount: number;
  isModerator: boolean;
  createdAt: number;         // Unix timestamp (секунды)
}

// ========== Logout ==========
export interface LogoutPayload {
  refresh: string;
}

export interface LogoutResponse {
  success: boolean;
  error?: string;
}

// ========== Moderator Request ==========
export interface ModeratorRequestPayload {
  message?: string;
}

export interface ModeratorRequestResponse {
  success: boolean;
  request?: {
    id: number;
    status: 'pending' | 'approved' | 'rejected';
    created_at: string;
  };
  error?: string;
}
```

---

## Примеры кода — React + TS

### Где хранить токены?

**Рекомендуемый способ (нормальный баланс между удобством и безопасностью):**
- **Access токен** → в памяти (React state / Context API)
- **Refresh токен** → в `localStorage` (для сохранения при обновлении страницы)

**Более безопасный способ (если много XSS рисков):**
- **Access токен** → в памяти
- **Refresh токен** → в httpOnly cookie (сервер управляет, браузер не может удалить через JS)

Мы используем **первый способ** в примерах ниже.

---

### 1️⃣ Создайте контекст для авторизации (AuthContext)

**`src/context/AuthContext.tsx`**

```tsx
import React, { createContext, useState, useContext, ReactNode } from 'react';
import { User, RegisterPayload, LoginPayload, RegisterResponse, LoginResponse } from '../types/auth';

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  
  // Функции
  login: (username: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
  setAccessToken: (token: string | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  
  // Загрузить токены из localStorage при запуске приложения
  React.useEffect(() => {
    const savedRefresh = localStorage.getItem('refreshToken');
    const savedAccess = localStorage.getItem('accessToken');
    if (savedAccess) {
      setAccessToken(savedAccess);
    }
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data: LoginResponse = await response.json();
      
      if (data.success && data.tokens && data.user) {
        setUser(data.user);
        setAccessToken(data.tokens.access);
        
        // Сохранить refresh в localStorage
        localStorage.setItem('refreshToken', data.tokens.refresh);
        localStorage.setItem('accessToken', data.tokens.access);
      } else {
        throw new Error(data.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (payload: RegisterPayload) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data: RegisterResponse = await response.json();
      
      if (data.success && data.user) {
        // После регистрации можно автоматически залогинить
        // или пусть пользователь сам логинится
        console.log('Registration successful', data.user);
      } else {
        throw new Error(data.error || 'Registration failed');
      }
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken && accessToken) {
        await fetch('http://127.0.0.1:8000/api/v1/auth/logout/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
          },
          body: JSON.stringify({ refresh: refreshToken })
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // В любом случае очистить локальное состояние
      setUser(null);
      setAccessToken(null);
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('accessToken');
    }
  };

  return (
    <AuthContext.Provider value={{ user, accessToken, refreshToken: localStorage.getItem('refreshToken'), login, register, logout, setUser, setAccessToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
};
```

---

### 2️⃣ Форма регистрации (с MUI)

**`src/components/RegisterForm.tsx`**

```tsx
import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Container,
  Typography
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { RegisterPayload } from '../types/auth';

export const RegisterForm: React.FC = () => {
  const { register } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState<RegisterPayload>({
    username: '',
    email: '',
    password: '',
    passwordConfirm: '',
    name: '',
    lastName: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      // Валидация на фронте
      if (formData.password !== formData.passwordConfirm) {
        throw new Error('Passwords do not match');
      }
      if (formData.password.length < 6) {
        throw new Error('Password must be at least 6 characters');
      }

      await register(formData);
      setSuccess(true);
      setFormData({ username: '', email: '', password: '', passwordConfirm: '', name: '', lastName: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Регистрация
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>Регистрация успешна! Теперь вы можете логиниться.</Alert>}

        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Имя"
            name="name"
            value={formData.name}
            onChange={handleChange}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Фамилия"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Username (никнейм)"
            name="username"
            value={formData.username}
            onChange={handleChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Пароль"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Повторите пароль"
            name="passwordConfirm"
            type="password"
            value={formData.passwordConfirm}
            onChange={handleChange}
            margin="normal"
            required
          />

          <Button
            fullWidth
            variant="contained"
            type="submit"
            sx={{ mt: 3 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Зарегистрироваться'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
};
```

---

### 3️⃣ Форма логина

**`src/components/LoginForm.tsx`**

```tsx
import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Container,
  Typography
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export const LoginForm: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      // Редирект на главную страницу после успешного логина
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Логин
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Username или Email"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Пароль"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
          />

          <Button
            fullWidth
            variant="contained"
            type="submit"
            sx={{ mt: 3 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Войти'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
};
```

---

### 4️⃣ Делать защищённые запросы (например, GET профиля)

**`src/api/apiClient.ts`**

```ts
// Функция для того, чтобы добавить Authorization заголовок
export const apiCall = async (
  url: string,
  options: RequestInit = {}
) => {
  const accessToken = localStorage.getItem('accessToken');

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  const response = await fetch(url, {
    ...options,
    headers
  });

  return response;
};

// Пример: получить профиль текущего пользователя
export const fetchMyProfile = async (userId: number) => {
  const response = await apiCall(
    `http://127.0.0.1:8000/auth/users/me/`,
    { method: 'GET' }
  );
  return response.json();
};
```

**Использование:**

```tsx
const { user } = useAuth();

React.useEffect(() => {
  if (user) {
    fetchMyProfile(user.id).then(data => {
      console.log('Profile:', data);
    });
  }
}, [user]);
```

---

### 5️⃣ Кнопка для выхода

**`src/components/LogoutButton.tsx`**

```tsx
import React from 'react';
import { Button } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export const LogoutButton: React.FC = () => {
  const { logout, accessToken } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = React.useState(false);

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!accessToken) {
    return null; // Не показывать кнопку, если не залогинен
  }

  return (
    <Button
      variant="outlined"
      onClick={handleLogout}
      disabled={loading}
    >
      {loading ? 'Выходим...' : 'Выход'}
    </Button>
  );
};
```

---

### 6️⃣ Заявка на модератора

**`src/components/ModeratorRequestForm.tsx`**

```tsx
import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { ModeratorRequestResponse } from '../types/auth';

export const ModeratorRequestForm: React.FC = () => {
  const { user, accessToken } = useAuth();
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    setOpen(false);
    setMessage('');
    setError('');
    setSuccess(false);
  };

  const handleSubmit = async () => {
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      if (!accessToken) {
        throw new Error('You must be logged in');
      }

      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/moderator-request/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({ message })
      });

      const data: ModeratorRequestResponse = await response.json();

      if (data.success) {
        setSuccess(true);
        setMessage('');
        setTimeout(() => handleClose(), 2000);
      } else {
        throw new Error(data.error || 'Failed to submit request');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setLoading(false);
    }
  };

  // Не показываем, если уже модератор
  if (user?.isModerator) {
    return (
      <Box sx={{ p: 2, bgcolor: '#e8f5e9', borderRadius: 1 }}>
        <Typography>✅ Вы уже модератор!</Typography>
      </Box>
    );
  }

  return (
    <>
      <Button variant="contained" onClick={handleOpen}>
        Стать модератором
      </Button>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Заявка на модератора</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success">Заявка отправлена! Ждите решения админа.</Alert>}

          {!success && (
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Почему вы хотите быть модератором?"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              margin="normal"
              placeholder="Напишите причину (опционально)"
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Отмена</Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Отправить'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
```

---

## Как работают токены

### Что такое Access Token?

```
Access Token = пропуск для входа
- живёт 15 минут
- нужно добавлять в заголовок для защищённых запросов
- истекает со временем
```

**Пример:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Что такое Refresh Token?

```
Refresh Token = билет для получения нового Access Token
- живёт 1 день
- не отправляем в заголовках обычных запросов
- используем только для получения нового access token
```

### Когда Access Token истёк?

**Если вы получили 401 Unauthorized:**

```ts
// Попробовать обновить access token
const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('refreshToken');

  const response = await fetch('http://127.0.0.1:8000/auth/jwt/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken })
  });

  const data = await response.json();
  if (data.access) {
    localStorage.setItem('accessToken', data.access);
    return data.access;
  }
};
```

---

## Cookie vs LocalStorage

### LocalStorage (то что мы используем по умолчанию)

**Плюсы:**
- Простой и понятный способ
- Можно читать из JavaScript
- Хранится между закрытиями браузера

**Минусы:**
- Уязвим для XSS атак (если код вредоноса на сайте, может украсть токены)

**Как использовать:**
```ts
// Сохранить
localStorage.setItem('accessToken', token);

// Получить
const token = localStorage.getItem('accessToken');

// Удалить
localStorage.removeItem('accessToken');
```

---

### HttpOnly Cookie (более безопасный способ)

**Плюсы:**
- Защищён от XSS атак (JavaScript не может читать)
- Браузер автоматически отправляет в запросах

**Минусы:**
- Сложнее настраивать
- Требует CORS и `credentials: 'include'`

**Как использовать:**

При логине укажите `useCookie: true`:
```ts
const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // ← добавить это!
  body: JSON.stringify({ username, password, useCookie: true })
});
```

Тогда для всех запросов добавляйте `credentials: 'include'`:
```ts
const response = await fetch('http://127.0.0.1:8000/api/v1/movies/', {
  method: 'GET',
  credentials: 'include'  // ← браузер сам добавит cookie
});
```

**Рекомендация:** для учебного проекта используйте LocalStorage (проще), в продакшене перейдите на cookie + HTTPS.

---

## Частые ошибки и как их исправить

### ❌ Ошибка: "401 Unauthorized" при logout

**Проблема:** access token истёк

**Решение:** logout работает и без access token, можно просто отправить:
```ts
await fetch('http://127.0.0.1:8000/api/v1/auth/logout/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <любой токен или даже пустое значение>'
  },
  body: JSON.stringify({ refresh: refreshToken })
});
```

---

### ❌ Ошибка: "Passwords do not match"

**Проблема:** поле `passwordConfirm` не совпадает с `password`

**Решение:** проверьте, что обе переменные заполнены и совпадают:
```ts
if (formData.password !== formData.passwordConfirm) {
  // Показать ошибку
}
```

---

### ❌ Ошибка: "Invalid credentials"

**Проблема:** неправильный username/email или пароль

**Решение:** 
- Проверьте, что username существует (или используйте email)
- Пароль вводится правильно
- Регистр букв в username имеет значение

---

### ❌ Ошибка: "401 Unauthorized" при защищённом запросе

**Проблема:** забыли добавить Authorization заголовок

**Решение:**
```ts
const accessToken = localStorage.getItem('accessToken');
const headers = {
  'Authorization': `Bearer ${accessToken}`  // ← добавить это!
};
```

---

### ❌ Ошибка: "You already have a pending moderator request"

**Проблема:** пользователь уже отправил заявку на модератора

**Решение:** нужно дождаться, пока админ её рассмотрит (одобрит или отклонит)

---

### ❌ CORS ошибка при регистрации

**Проблема:** запрос блокирован браузером (CORS)

**Решение:** это может быть, если URL неправильный. Проверьте:
```ts
// ✅ Правильно
http://127.0.0.1:8000/api/v1/auth/register/

// ❌ Неправильно
http://127.0.0.1:8000/register/
http://localhost:8000/api/v1/auth/register/
```

---

## Итоговая схема (как всё вместе работает)

```
1. Пользователь открывает сайт
   ↓
2. Проверяем localStorage на refreshToken
   ├─ если есть → используем его
   └─ если нет → показываем Login форму
   ↓
3. Пользователь вводит username и пароль → нажимает "Войти"
   ↓
4. Отправляем POST /api/v1/auth/login/
   ↓
5. Сервер возвращает access и refresh токены
   ↓
6. Сохраняем их (access в памяти, refresh в localStorage)
   ↓
7. Теперь можем делать защищённые запросы (с Authorization заголовком)
   ↓
8. Если access истёк (получили 401), обновляем его через refresh
   ↓
9. Когда пользователь нажимает "Выход", отправляем логаут
   ↓
10. Удаляем токены из памяти и localStorage
```

---

## Чек-лист перед продакшеном

- [ ] API URL не захардкодирован (используется .env переменная)
- [ ] Токены хранятся правильно (access в памяти или localStorage, refresh в cookie)
- [ ] На всех защищённых запросах добавлен Authorization заголовок
- [ ] Обработаны ошибки 401 (refresh expired) и 403 (недостаточно прав)
- [ ] Форма валидирует пароль перед отправкой
- [ ] После logout удаляются ВСЕ токены
- [ ] Используется HTTPS в продакшене (не HTTP!)
- [ ] Установлены флаги cookie: Secure, HttpOnly, SameSite=Strict

---

## Вопросы?

Если что-то не понимаете:
1. Посмотрите пример в `docs/auth_test.html` (можно открыть в браузере и тестировать API)
2. Проверьте вывод сервера в консоли (там будут ошибки)
3. Включите DevTools → Network → смотрите request/response
