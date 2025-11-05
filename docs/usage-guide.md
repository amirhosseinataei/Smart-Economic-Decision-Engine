# راهنمای استفاده از SEDE

<div dir="rtl">

## نصب و راه‌اندازی

### 1. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 2. تنظیم پیکربندی

فایل `config/config.yaml` را ویرایش کنید و تنظیمات مورد نظر خود را اعمال کنید.

### 3. اجرای مثال‌ها

```bash
python examples/usage_example.py
```

## استفاده از چت‌بات

### استفاده ساده

```python
from src.chatbot import ChatbotEngine

engine = ChatbotEngine()
response = engine.process_message(
    "من 600 میلیون نقد دارم و می‌خواهم خانه در تهران رهن کنم"
)

print(response.message)
print(response.query)
```

### استفاده پیشرفته

```python
from src.chatbot import ChatbotEngine

engine = ChatbotEngine()

# پردازش با session tracking
response = engine.process_message(
    "من 600 میلیون نقد دارم",
    session_id="user_123"
)

# ادامه مکالمه
response2 = engine.process_message(
    "می‌خواهم خانه در تهران اکباتان رهن کنم",
    session_id="user_123"
)
```

## استفاده از خزنده

### خزیدن یک سایت

```python
from src.crawler import CrawlerManager

manager = CrawlerManager()

# خزیدن دیوار
result = manager.crawl_site(
    'divar',
    filters={
        'category': 'apartment-rent',
        'location': 'تهران',
        'price_max': 800
    }
)

print(f"Found {result.total_items} items")
```

### خزیدن چندین سایت

```python
from src.crawler import CrawlerManager

manager = CrawlerManager()

queries = [
    {
        'site': 'divar',
        'filters': {'category': 'apartment-rent', 'price_max': 800},
        'goal_id': 1
    },
    {
        'site': 'sheypoor',
        'filters': {'category': 'apartment-rent', 'price_max': 800},
        'goal_id': 1
    }
]

batch_result = manager.crawl_batch(queries, parallel=True)
print(f"Total items: {batch_result.total_items}")
```

## استفاده یکپارچه (Chatbot + Crawler)

```python
from src.integration import SEDEIntegration

sede = SEDEIntegration()

# پردازش درخواست کامل کاربر
result = sede.process_user_request(
    "سلام من 600 میلیون نقد دارم و می‌خواهم خانه در تهران اکباتان رهن کنم",
    session_id="user_123"
)

# نتایج
print(f"Items found: {result['crawl_results']['total_items']}")
print(f"Sources: {result['crawl_results']['sources']}")

# ذخیره نتایج
import json
with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

## استفاده از Command Line

### حالت Interactive

```bash
python -m src.main --interactive
```

### پردازش یک پیام

```bash
python -m src.main --message "من 60 میلیون پول دارم چطور می‌توانم یک مدل گوشی مناسب تهیه کنم"
```

## نکات مهم

1. **Selenium**: برای برخی سایت‌ها (مثل دیوار) نیاز به ChromeDriver است
2. **Rate Limiting**: بین درخواست‌ها تاخیر وجود دارد تا از IP ban جلوگیری شود
3. **Error Handling**: همیشه خطاها را مدیریت کنید
4. **Cleanup**: بعد از استفاده، `cleanup()` را فراخوانی کنید

## مثال‌های پیشرفته

مثال‌های کامل در پوشه `examples/` موجود است.

</div>

