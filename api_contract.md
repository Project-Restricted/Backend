# 🎬 Movies API

## 🔹 GET /api/v1/movies/

Возвращает список фильмов с возможностью поиска, пагинации и фильтрации по тегам, году и стране.

### 📥 Параметры запроса

| Параметр       | Тип       | Обязательный | Описание |
|----------------|------------|---------------|-----------|
| `page`         | integer    | ❌            | Номер страницы (по умолчанию `1`) |
| `search`       | string     | ❌            | Поиск по названию фильма |
| `tags`         | string     | ❌            | Список тегов, разделённых запятыми (например, `action,thriller`) |
| `exclude_tags` | string     | ❌            | Теги, которые нужно исключить (например, `-comedy,-romance`) |
| `year`         | integer    | ❌            | Фильтрация по году |
| `country`      | string     | ❌            | Название страны |

---

### 📤 Пример запроса
```http
GET /api/v1/movies/?search=inception&page=1
```

### 📤 Пример ответа
```
{
  "count": 245,
  "next": "https://api.cinemaportal.com/api/v1/movies/?page=2",
  "previous": null,
  "results": [
    {
      "id": 14,
      "title": "The Batman",
      "year": 2022,
      "duration": "02:56:00",
      "rating": 7.9,
      "poster_url": "https://cdn.cinemaportal.com/posters/batman.jpg",
      "genres": ["Action", "Crime", "Drama"]
    },
    {
      "id": 42,
      "title": "Inception",
      "year": 2010,
      "duration": "02:28:00",
      "rating": 8.8,
      "poster_url": "https://cdn.cinemaportal.com/posters/inception.jpg",
      "genres": ["Sci-Fi", "Thriller"]
    }
  ]
}
```

## 🔹 GET /api/v1/movies/{id}/`

Возвращает детальную информацию о фильме по его ID.

### 📥 Параметры запроса
| Параметр | Тип | Обязательный | Описание |
|-----------|-----|---------------|-----------|
| `id` | integer | ✅ | Уникальный идентификатор фильма |

### 📤 Пример запроса
```http
GET /api/v1/movies/42/
```
### 📤 Пример ответа
```
{
  "id": 42,
  "title": "Inception",
  "year": 2010,
  "genres": ["Sci-Fi", "Thriller"],
  "director": {"id": 7, "name": "Christopher Nolan"},
  "actors": [
    {"id": 101, "name": "Leonardo DiCaprio"},
    {"id": 102, "name": "Joseph Gordon-Levitt"}
  ],
  "description": "A thief who steals corporate secrets through dream-sharing technology...",
  "rating": 8.8,
  "reviews_count": 240,
  "trailer_url": "https://youtu.be/YoHD9XEInc0",
  "available_on": [
    {"platform": "VK", "url": "https://vk.com/inception"},
    {"platform": "RuTube", "url": "https://rutube.com/inception"}
  ]
}
```
