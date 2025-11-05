# ساختار پروژه SEDE

```
Smart Economic Decision Engine/
├── config/                      # فایل‌های پیکربندی
│   └── config.yaml             # تنظیمات اصلی
│
├── data/                        # داده‌های جمع‌آوری شده
│   └── .gitkeep
│
├── docs/                        # مستندات
│   ├── architecture.md         # معماری سیستم
│   ├── api.md                  # مستندات API
│   ├── business-plan.md        # بیزنس پلن
│   ├── development.md          # راهنمای توسعه
│   └── usage-guide.md          # راهنمای استفاده
│
├── examples/                    # مثال‌های استفاده
│   └── usage_example.py        # مثال‌های کامل
│
├── logs/                        # فایل‌های لاگ
│   └── .gitkeep
│
├── src/                         # کد منبع
│   ├── chatbot/                # ماژول چت‌بات
│   │   ├── engine.py           # موتور اصلی چت‌بات
│   │   ├── nlu.py              # پردازش زبان طبیعی
│   │   ├── entity_extractor.py # استخراج موجودیت
│   │   ├── intent_classifier.py# طبقه‌بندی مقصود
│   │   ├── query_generator.py  # تولید کوئری
│   │   └── schemas.py          # اسکیماها
│   │
│   ├── crawler/                # ماژول خزنده
│   │   ├── base_crawler.py     # کلاس پایه خزنده
│   │   ├── crawler_manager.py  # مدیریت خزنده‌ها
│   │   ├── data_normalizer.py  # نرمال‌سازی داده
│   │   ├── divar_crawler.py    # خزنده دیوار
│   │   ├── sheypoor_crawler.py # خزنده شیپور
│   │   ├── bama_crawler.py     # خزنده باما
│   │   ├── torob_crawler.py    # خزنده ترب
│   │   ├── digikala_crawler.py # خزنده دیجی‌کالا
│   │   └── schemas.py          # اسکیماها
│   │
│   ├── utils/                  # ابزارهای کمکی
│   │   ├── logger.py           # مدیریت لاگ
│   │   └── config_loader.py    # بارگذاری تنظیمات
│   │
│   ├── integration.py          # یکپارچه‌سازی چت‌بات و خزنده
│   └── main.py                 # نقطه ورود اصلی
│
├── tests/                       # تست‌ها
│   ├── test_chatbot.py         # تست چت‌بات
│   └── __init__.py
│
├── .gitignore                   # فایل‌های نادیده گرفته شده
├── CONTRIBUTING.md              # راهنمای مشارکت
├── PROJECT_STRUCTURE.md         # این فایل
├── README.md                    # فایل اصلی README
├── requirements.txt             # وابستگی‌های Python
└── setup.py                     # نصب پکیج
```

## توضیحات بخش‌ها

### `src/chatbot/`
سیستم چت‌بات هوشمند که درخواست‌های کاربر را به زبان طبیعی پردازش می‌کند و به کوئری‌های ساختاریافته تبدیل می‌کند.

### `src/crawler/`
سیستم خزنده چندسایته که از سایت‌های مختلف (دیوار، شیپور، باما، ترب، دیجی‌کالا) داده جمع‌آوری می‌کند.

### `src/integration.py`
کلاس اصلی که چت‌بات و خزنده را به هم متصل می‌کند و جریان کامل کار را مدیریت می‌کند.

### `examples/`
مثال‌های کامل استفاده از سیستم برای درک بهتر نحوه کار.

### `docs/`
مستندات کامل پروژه شامل معماری، API، و راهنماهای استفاده.

