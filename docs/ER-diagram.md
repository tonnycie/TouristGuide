# ER диаграма

```mermaid
erDiagram
    USER ||--o{ ROUTE : "публикува"
    USER ||--o{ REVIEW : "пише"
    ROUTE ||--|{ WAYPOINT : "съдържа"
    ROUTE ||--o{ PHOTO : "има"
    ROUTE ||--o{ REVIEW : "получава"

    USER {
        int id PK
        string username
        string email
        string password "хеширана"
        datetime date_joined
    }
    ROUTE {
        int id PK
        int author_id FK
        string title
        string destination
        text description "лични впечатления"
        text tips "съвети за пътуване"
        datetime created_at
    }
    WAYPOINT {
        int id PK
        int route_id FK
        string name
        decimal latitude "9,6 знака, от -90 до 90"
        decimal longitude "9,6 знака, от -180 до 180"
        int order_index "ред в маршрута"
    }
    PHOTO {
        int id PK
        int route_id FK
        string image "път до файла"
    }
    REVIEW {
        int id PK
        int route_id FK
        int author_id FK
        text text
        int rating "1 до 5"
        datetime created_at
    }
```

## Ограничения
- Един потребител може да остави **само един отзив** на маршрут (уникална двойка `route`, `author`).
- Автор на маршрут не може да оценява собствения си маршрут (проверка в API-то).
- При изтриване на маршрут се изтриват каскадно точките, снимките и отзивите му.
- Географските координати се пазят като десетични числа с 6 знака след запетаята (около 0,1 м точност), по една точка на ред.