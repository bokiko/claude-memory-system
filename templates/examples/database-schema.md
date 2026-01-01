---
title: Database Schema Template
category: databases
tags: [database, schema, sql, template]
---

# Database: main_db

Connection: `postgresql://user:pass@host:5432/main_db`

## Tables

### users

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | Primary key |
| email | varchar(255) | Unique, indexed |
| name | varchar(100) | |
| created_at | timestamp | Default now() |
| updated_at | timestamp | |

### orders

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | Primary key |
| user_id | uuid | FK → users.id |
| status | enum | pending, paid, shipped, delivered |
| total | decimal(10,2) | |
| created_at | timestamp | |

## Indexes

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
```

## Common Queries

### Get user with orders

```sql
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.id = $1
GROUP BY u.id;
```

### Recent orders

```sql
SELECT * FROM orders
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 100;
```

## Migrations

```bash
# Run pending migrations
npm run migrate

# Rollback last migration
npm run migrate:rollback

# Create new migration
npm run migrate:create add_users_table
```
