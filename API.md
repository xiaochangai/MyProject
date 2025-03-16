# 记账系统API文档

## 基础信息

- 基础URL: `http://localhost:8000`
- 所有需要认证的接口都需要在请求头中携带 `Authorization: Bearer <token>` 
- 所有响应都是JSON格式

## 认证相关接口

### 用户注册

- URL: `/api/auth/register`
- 方法: `POST`
- 认证要求: 无

请求体：
```json
{
    "username": "string",
    "password": "string"
}
```

响应示例：
```json
{
    "message": "注册成功",
    "user": {
        "id": 1,
        "username": "string",
        "created_at": "2023-09-20 10:00:00"
    }
}
```

### 用户登录

- URL: `/api/auth/login`
- 方法: `POST`
- 认证要求: 无

请求体：
```json
{
    "username": "string",
    "password": "string"
}
```

响应示例：
```json
{
    "message": "登录成功",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "string",
        "created_at": "2023-09-20 10:00:00"
    }
}
```

### 获取当前用户信息

- URL: `/api/auth/me`
- 方法: `GET`
- 认证要求: 需要

响应示例：
```json
{
    "id": 1,
    "username": "string",
    "created_at": "2023-09-20 10:00:00"
}
```

## 交易记录接口

### 获取交易记录列表

- URL: `/api/transactions`
- 方法: `GET`
- 认证要求: 需要

响应示例：
```json
[
    {
        "id": 1,
        "amount": 100.0,
        "category": "餐饮",
        "description": "午餐",
        "date": "2023-09-20",
        "type": "expense",
        "created_at": "2023-09-20 10:00:00",
        "user_id": 1
    }
]
```

### 获取单个交易记录

- URL: `/api/transactions/<id>`
- 方法: `GET`
- 认证要求: 需要

响应示例：
```json
{
    "id": 1,
    "amount": 100.0,
    "category": "餐饮",
    "description": "午餐",
    "date": "2023-09-20",
    "type": "expense",
    "created_at": "2023-09-20 10:00:00",
    "user_id": 1
}
```

### 创建交易记录

- URL: `/api/transactions`
- 方法: `POST`
- 认证要求: 需要

请求体：
```json
{
    "amount": 100.0,
    "category": "餐饮",
    "description": "午餐",
    "date": "2023-09-20",
    "type": "expense"
}
```

响应示例：
```json
{
    "id": 1,
    "amount": 100.0,
    "category": "餐饮",
    "description": "午餐",
    "date": "2023-09-20",
    "type": "expense",
    "created_at": "2023-09-20 10:00:00",
    "user_id": 1
}
```

### 更新交易记录

- URL: `/api/transactions/<id>`
- 方法: `PUT`
- 认证要求: 需要

请求体：
```json
{
    "amount": 100.0,
    "category": "餐饮",
    "description": "午餐",
    "date": "2023-09-20",
    "type": "expense"
}
```

响应示例：
```json
{
    "id": 1,
    "amount": 100.0,
    "category": "餐饮",
    "description": "午餐",
    "date": "2023-09-20",
    "type": "expense",
    "created_at": "2023-09-20 10:00:00",
    "user_id": 1
}
```

### 删除交易记录

- URL: `/api/transactions/<id>`
- 方法: `DELETE`
- 认证要求: 需要

响应示例：
```json
{
    "message": "Transaction deleted"
}
```

## 统计接口

### 月度统计

- URL: `/api/statistics/monthly`
- 方法: `GET`
- 认证要求: 无

查询参数：
- `year`: 年份（可选，默认为当前年份）

响应示例：
```json
[
    {
        "month": 1,
        "income": 5000.0,
        "expense": 3000.0,
        "balance": 2000.0
    },
    // ... 其他月份
]
```

### 年度统计

- URL: `/api/statistics/yearly`
- 方法: `GET`
- 认证要求: 无

响应示例：
```json
[
    {
        "year": 2023,
        "income": 60000.0,
        "expense": 36000.0,
        "balance": 24000.0
    },
    // ... 其他年份
]
```

### 分类统计

- URL: `/api/statistics/categories`
- 方法: `GET`
- 认证要求: 无

查询参数：
- `year`: 年份（可选，默认为当前年份）
- `month`: 月份（可选，默认为当前月份）

响应示例：
```json
[
    {
        "category": "餐饮",
        "amount": 1500.0
    },
    // ... 其他类别
]
```