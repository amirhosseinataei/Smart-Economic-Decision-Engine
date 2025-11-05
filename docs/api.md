# مستندات API

<div dir="rtl">

## 🔌 API Endpoints

### 1. Chatbot API

#### POST `/api/v1/chatbot/query`

دریافت درخواست کاربر و تبدیل به کوئری ساختاریافته

**Request Body:**
```json
{
  "message": "سلام من 600 میلیون نقد دارم و می‌خواهم خانه در تهران اکباتان رهن کنم",
  "session_id": "user_session_123",
  "context": {}
}
```

**Response:**
```json
{
  "success": true,
  "query": {
    "user_profile": {
      "liquidity": 600000000,
      "loan_amount": 0,
      "max_monthly_payment": 0
    },
    "search_goals": [
      {
        "goal_id": 1,
        "type": "residential_rent",
        "target_location": "تهران، اکباتان",
        "budget_source": "liquidity",
        "priority": "high",
        "search_type": "رهن کامل"
      }
    ]
  },
  "confidence": 0.92
}
```

### 2. Search API

#### POST `/api/v1/search/execute`

اجرای جستجو بر اساس کوئری ساختاریافته

**Request Body:**
```json
{
  "query": {
    "search_goals": [...]
  },
  "sites": ["divar", "sheypoor", "bama"]
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "divar": [...],
    "sheypoor": [...],
    "bama": [...]
  },
  "total_items": 150,
  "execution_time": 12.5
}
```

### 3. Analysis API

#### POST `/api/v1/analysis/fraud-detection`

تحلیل آگهی‌ها برای تشخیص تقلب

**Request Body:**
```json
{
  "items": [...]
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "fraud_score": 0.15,
    "risk_level": "low",
    "flagged_items": []
  }
}
```

</div>

