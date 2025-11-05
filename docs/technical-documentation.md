# مستندات فنی کامل - SEDE
## نمونه اجرای کامل سیستم با جزئیات پیشرفته

<div dir="rtl">

---

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [درخواست نمونه کاربر](#درخواست-نمونه-کاربر)
3. [مرحله 1: پردازش اولیه چت‌بات](#مرحله-1-پردازش-اولیه-چت‌بات)
4. [مرحله 2: استخراج موجودیت‌ها](#مرحله-2-استخراج-موجودیت‌ها)
5. [مرحله 3: طبقه‌بندی مقصود](#مرحله-3-طبقه‌بندی-مقصود)
6. [مرحله 4: تولید کوئری ساختاریافته](#مرحله-4-تولید-کوئری-ساختاریافته)
7. [مرحله 5: اجرای خزنده](#مرحله-5-اجرای-خزنده)
8. [مرحله 6: نرمال‌سازی داده‌ها](#مرحله-6-نرمال‌سازی-داده‌ها)
9. [نتایج نهایی](#نتایج-نهایی)
10. [نمودار جریان کامل](#نمودار-جریان-کامل)

---

## 🎯 مقدمه

این مستندات نشان می‌دهد که چگونه سیستم SEDE یک درخواست پیچیده کاربر را پردازش کرده و به داده‌های قابل استفاده تبدیل می‌کند.

### معماری کلی

```
User Input → Chatbot Engine → NLU Processing → Query Generation → Crawler Execution → Data Normalization → Results
```

---

## 📝 درخواست نمونه کاربر

### ورودی اصلی

```
سلام من 600 میلیون نقد دارم و می‌توانم 200 میلیون هم وام بگیرم تا 2 ماه آینده به دستم برسد.
می‌خواهم بررسی کنم با این مبلغ خانه در تهران اکباتان رهن کنم.
اگر نمی‌توانم در کدام منطقه مناسب می‌توانم منزل برای رهن پیدا کنم.
همچنین اگر پول من نمی‌رسد برای ماشین چطور می‌توانم ماشین مناسبی با این مبلغ تهیه کنم.
همچنین چه برای اجاره و چه برای قسط ماشین لیزینگ می‌توانم ماهی 15 میلیون بدهم بجز نقدینگی و مبلغ وامم.
```

### تحلیل اولیه درخواست

- **نقدینگی**: 600 میلیون تومان
- **وام**: 200 میلیون تومان (2 ماه آینده)
- **توان پرداخت ماهیانه**: 15 میلیون تومان
- **اهداف**: 
  1. رهن خانه در اکباتان (اولویت بالا)
  2. رهن خانه در منطقه جایگزین (اولویت متوسط)
  3. خرید یا لیزینگ خودرو (اولویت بالا)

---

## 🔄 مرحله 1: پردازش اولیه چت‌بات

### کلاس: `ChatbotEngine`

```python
# فایل: src/chatbot/engine.py

class ChatbotEngine:
    def process_message(self, message: str, session_id: str = None):
        # Step 1.1: دریافت پیام کاربر
        user_message = message
        
        # Step 1.2: استخراج context از session (اگر وجود داشته باشد)
        context = self._get_conversation_context(session_id)
        
        # Step 1.3: ارسال به NLU Processor
        nlu_result = self.nlu_processor.process(message, context)
```

### خروجی مرحله 1

```json
{
  "message_received": true,
  "session_id": "user_session_12345",
  "message_length": 287,
  "timestamp": "2024-11-15T10:30:00"
}
```

---

## 🔍 مرحله 2: استخراج موجودیت‌ها

### کلاس: `EntityExtractor`

```python
# فایل: src/chatbot/entity_extractor.py

class EntityExtractor:
    def extract_all_entities(self, text: str):
        # Step 2.1: استخراج موجودیت‌های پولی
        money_entities = self.extract_money_entities(text)
        # Result: [600 میلیون, 200 میلیون, 15 میلیون]
        
        # Step 2.2: استخراج اطلاعات وام
        loan_amount, loan_months = self.extract_loan_info(text)
        # Result: (200.0, 2)
        
        # Step 2.3: استخراج پرداخت ماهیانه
        monthly_payment = self.extract_monthly_payment(text)
        # Result: 15.0
        
        # Step 2.4: استخراج مکان‌ها
        locations = self.extract_location(text)
        # Result: ["تهران", "اکباتان"]
        
        # Step 2.5: استخراج نوع جستجو
        search_type = self.extract_search_type(text)
        # Result: {"type": "residential_rent", "search_type": "رهن کامل"}
```

### جزئیات استخراج موجودیت‌های پولی

#### الگوهای Regex استفاده شده:

```python
money_patterns = [
    r'(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون|م|M)\s*(?:تومان|تومن)?',
    r'(\d+(?:\.\d+)?)\s*(?:هزار|k)\s*(?:تومان|تومن)?',
    r'(\d+(?:\.\d+)?)\s*(?:میلیارد|بیلیون|b)\s*(?:تومان|تومن)?',
]
```

#### نتایج استخراج:

| موجودیت | مقدار خام | مقدار نرمال‌سازی شده | موقعیت در متن | اطمینان |
|---------|-----------|---------------------|---------------|---------|
| نقدینگی | "600 میلیون" | 600.0 | 12-25 | 0.95 |
| وام | "200 میلیون" | 200.0 | 45-60 | 0.90 |
| پرداخت ماهیانه | "ماهی 15 میلیون" | 15.0 | 250-265 | 0.85 |

### خروجی مرحله 2

```json
{
  "entities": {
    "money_entities": [
      {
        "entity_type": "money",
        "value": 600.0,
        "confidence": 0.95,
        "start_pos": 12,
        "end_pos": 25,
        "raw_text": "600 میلیون"
      },
      {
        "entity_type": "money",
        "value": 200.0,
        "confidence": 0.90,
        "start_pos": 45,
        "end_pos": 60,
        "raw_text": "200 میلیون"
      },
      {
        "entity_type": "money",
        "value": 15.0,
        "confidence": 0.85,
        "start_pos": 250,
        "end_pos": 265,
        "raw_text": "ماهی 15 میلیون"
      }
    ],
    "locations": ["تهران", "اکباتان"],
    "loan_info": {
      "amount": 200.0,
      "availability_months": 2
    },
    "monthly_payment": 15.0,
    "search_type": {
      "type": "residential_rent",
      "search_type": "رهن کامل",
      "is_rent": true,
      "is_purchase": false,
      "is_lease": false
    },
    "primary_liquidity": 600.0
  }
}
```

---

## 🎯 مرحله 3: طبقه‌بندی مقصود

### کلاس: `IntentClassifier`

```python
# فایل: src/chatbot/intent_classifier.py

class IntentClassifier:
    def classify(self, text: str):
        # Step 3.1: طبقه‌بندی بر اساس کلمات کلیدی
        keyword_scores = self.classify_by_keywords(text)
        # Result: [("search", 0.85), ("advice", 0.45)]
        
        # Step 3.2: طبقه‌بندی بر اساس الگوها
        pattern_scores = self.classify_by_patterns(text)
        # Result: [("search", 0.90)]
        
        # Step 3.3: ترکیب نتایج
        final_intent, confidence = self._merge_scores(keyword_scores, pattern_scores)
        # Result: ("search", 0.92)
```

### تحلیل کلمات کلیدی

| کلمه کلیدی | نوع مقصود | امتیاز |
|------------|-----------|--------|
| "می‌خواهم" | SEARCH | 0.3 |
| "بررسی" | SEARCH | 0.2 |
| "پیدا کنم" | SEARCH | 0.25 |
| "چطور" | ADVICE | 0.15 |
| "می‌توانم" | CALCULATE | 0.1 |

### خروجی مرحله 3

```json
{
  "intent": "search",
  "confidence": 0.92,
  "requires_clarification": false,
  "classification_details": {
    "keyword_score": 0.85,
    "pattern_score": 0.90,
    "final_score": 0.92
  }
}
```

---

## 🏗️ مرحله 4: تولید کوئری ساختاریافته

### کلاس: `NLUProcessor`

```python
# فایل: src/chatbot/nlu.py

class NLUProcessor:
    def process(self, text: str, context: dict = None):
        # Step 4.1: ساخت UserProfile
        user_profile = self.entity_extractor.build_user_profile(entities)
        # Result: UserProfile(liquidity=600, loan_amount=200, ...)
        
        # Step 4.2: ساخت SearchGoals
        search_goals = self.entity_extractor.build_search_goals(entities, user_profile)
        # Result: [Goal1, Goal2, Goal3]
        
        # Step 4.3: محاسبه confidence
        overall_confidence = self._calculate_confidence(...)
        # Result: 0.88
```

### ساخت UserProfile

```json
{
  "user_profile": {
    "liquidity": 600000000.0,
    "loan_amount": 200000000.0,
    "loan_availability_months": 2,
    "max_monthly_payment": 15000000.0,
    "existing_obligations": 0.0,
    "total_budget": 800000000.0,
    "effective_monthly_budget": 15000000.0
  }
}
```

### ساخت SearchGoals

```json
{
  "search_goals": [
    {
      "goal_id": 1,
      "type": "residential_rent",
      "target_location": "تهران، اکباتان",
      "budget_source": "liquidity + loan",
      "priority": "high",
      "search_type": "رهن کامل",
      "max_price": 800000000.0,
      "max_monthly_lease_payment": null,
      "additional_filters": {}
    },
    {
      "goal_id": 2,
      "type": "residential_rent",
      "target_location": "تهران، منطقه مناسب پیشنهادی",
      "budget_source": "liquidity + loan",
      "priority": "medium",
      "search_type": "رهن کامل",
      "max_price": 800000000.0,
      "max_monthly_lease_payment": null,
      "additional_filters": {}
    },
    {
      "goal_id": 3,
      "type": "vehicle_purchase_or_lease",
      "target_location": "Any",
      "budget_source": "liquidity",
      "max_monthly_lease_payment": 15000000.0,
      "priority": "high",
      "search_type": "خرید یا لیزینگ",
      "max_price": 800000000.0,
      "additional_filters": {}
    }
  ],
  "is_multi_goal": true
}
```

### کلاس: `QueryGenerator`

```python
# فایل: src/chatbot/query_generator.py

class QueryGenerator:
    def generate_queries(self, structured_query: StructuredQuery):
        # Step 4.4: برای هر goal، کوئری‌های سایت‌های مختلف تولید می‌شود
        
        # Goal 1: رهن اکباتان
        # - Divar: apartment-rent, location=اکباتان, price_max=800
        # - Sheypoor: apartment-rent, location=اکباتان, price_max=800
        
        # Goal 3: خودرو
        # - Bama: search_type=purchase, price_max=800
        # - Torob: product_name=خودرو, price_max=800
```

### خروجی Query Generator

```json
{
  "queries": [
    {
      "site": "divar",
      "goal_id": 1,
      "search_type": "rent",
      "filters": {
        "category": "apartment-rent",
        "location": "تهران، اکباتان",
        "price_max": 800,
        "price_min": 640,
        "rent_type": "full_deposit"
      },
      "priority": 3,
      "metadata": {
        "goal_type": "residential_rent",
        "target_location": "تهران، اکباتان",
        "budget_source": "liquidity + loan"
      }
    },
    {
      "site": "sheypoor",
      "goal_id": 1,
      "search_type": "rent",
      "filters": {
        "category": "apartment-rent",
        "location": "تهران، اکباتان",
        "price_max": 800,
        "price_min": 640
      },
      "priority": 3,
      "metadata": {
        "goal_type": "residential_rent",
        "target_location": "تهران، اکباتان",
        "budget_source": "liquidity + loan"
      }
    },
    {
      "site": "torob",
      "goal_id": 3,
      "search_type": "general",
      "filters": {
        "product_name": "گوشی موبایل",
        "price_max": 60,
        "price_min": 40
      },
      "priority": 3,
      "metadata": {
        "goal_type": "electronics",
        "target_location": "Any",
        "budget_source": "liquidity"
      }
    }
  ],
  "total_queries": 5,
  "sites": ["divar", "sheypoor", "bama", "torob", "digikala"]
}
```

---

## 🕷️ مرحله 5: اجرای خزنده

### کلاس: `CrawlerManager`

```python
# فایل: src/crawler/crawler_manager.py

class CrawlerManager:
    def crawl_from_query_json(self, query_json: dict):
        # Step 5.1: تبدیل کوئری‌ها به فرمت خزنده
        crawl_queries = self._convert_queries(query_json)
        
        # Step 5.2: اجرای موازی خزنده‌ها
        batch_result = self.crawl_batch(crawl_queries, parallel=True)
        
        # Step 5.3: نرمال‌سازی نتایج
        normalized = self.normalizer.normalize_batch(batch_result)
```

### اجرای خزنده Torob (مثال)

#### کلاس: `TorobCrawler`

```python
# فایل: src/crawler/torob_crawler.py

class TorobCrawler(BaseCrawler):
    def build_search_url(self, filters: dict):
        # Step 5.1.1: ساخت URL
        product_name = filters.get('product_name', 'گوشی موبایل')
        price_max = filters.get('price_max', 60)
        
        url = f"https://torob.com/search/{product_name}"
        url += f"?price-max={int(price_max * 1000000)}"
        
        return url
    
    def extract_items(self, html_content: str):
        # Step 5.1.2: استخراج آیتم‌ها از HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        product_cards = soup.find_all('div', class_='product-card')
        
        items = []
        for card in product_cards:
            # استخراج اطلاعات هر محصول
            item = {
                'title': extract_title(card),
                'price': extract_price(card),
                'url': extract_url(card),
                'image': extract_image(card),
                ...
            }
            items.append(item)
        
        return items
```

### جزئیات اجرای خزنده Torob

#### URL تولید شده:
```
https://torob.com/search/گوشی-موبایل?price-max=60000000&price-min=40000000
```

#### الگوی HTML مورد استفاده:
```html
<div class="product-card">
    <h3 class="product-title">
        <a href="/product/123456">گوشی سامسونگ Galaxy S23</a>
    </h3>
    <div class="product-price">55,000,000 تومان</div>
    <img src="https://torob.com/images/product.jpg" />
</div>
```

#### نتایج استخراج (100 آیتم):

```json
{
  "success": true,
  "site_name": "torob",
  "items": [
    {
      "item_id": "torob_123456",
      "source_site": "torob",
      "title": "گوشی موبایل سامسونگ Galaxy S23 Ultra 256GB",
      "description": "گوشی سامسونگ گلکسی S23 اولترا با حافظه 256 گیگابایت",
      "url": "https://torob.com/product/123456",
      "price": 55.5,
      "price_text": "55,500,000 تومان",
      "price_type": "نقدی",
      "location": null,
      "city": null,
      "district": null,
      "images": [
        "https://torob.com/images/product-123456-1.jpg",
        "https://torob.com/images/product-123456-2.jpg"
      ],
      "thumbnail": "https://torob.com/images/product-123456-thumb.jpg",
      "properties": {
        "product_type": "electronics",
        "brand": "Samsung",
        "model": "Galaxy S23 Ultra",
        "storage": "256GB",
        "color": "Black",
        "raw_data": {
          "original_html": "...",
          "extracted_fields": {...}
        }
      },
      "crawled_at": "2024-11-15T10:35:23.456789",
      "goal_id": 3,
      "search_query": {
        "site": "torob",
        "filters": {
          "product_name": "گوشی موبایل",
          "price_max": 60,
          "price_min": 40
        }
      },
      "confidence_score": 0.85,
      "completeness_score": 0.92
    },
    {
      "item_id": "torob_123457",
      "source_site": "torob",
      "title": "گوشی موبایل اپل iPhone 14 Pro 256GB",
      "description": "گوشی اپل آیفون 14 پرو با حافظه 256 گیگابایت",
      "url": "https://torob.com/product/123457",
      "price": 58.2,
      "price_text": "58,200,000 تومان",
      "price_type": "نقدی",
      "images": [
        "https://torob.com/images/product-123457-1.jpg"
      ],
      "thumbnail": "https://torob.com/images/product-123457-thumb.jpg",
      "properties": {
        "product_type": "electronics",
        "brand": "Apple",
        "model": "iPhone 14 Pro",
        "storage": "256GB",
        "color": "Deep Purple"
      },
      "crawled_at": "2024-11-15T10:35:24.123456",
      "goal_id": 3,
      "confidence_score": 0.88,
      "completeness_score": 0.95
    }
    // ... 98 آیتم دیگر
  ],
  "total_items": 100,
  "execution_time": 12.45,
  "errors": []
}
```

### آمار اجرای خزنده

| سایت | تعداد آیتم‌ها | زمان اجرا (ثانیه) | خطاها | موفقیت |
|------|---------------|-------------------|-------|--------|
| Torob | 100 | 12.45 | 0 | ✅ |
| Divar | 45 | 18.32 | 0 | ✅ |
| Sheypoor | 38 | 15.67 | 1 | ✅ |
| Bama | 52 | 20.11 | 0 | ✅ |
| Digikala | 67 | 14.89 | 0 | ✅ |
| **مجموع** | **302** | **81.44** | **1** | **✅** |

---

## 🔄 مرحله 6: نرمال‌سازی داده‌ها

### کلاس: `DataNormalizer`

```python
# فایل: src/crawler/data_normalizer.py

class DataNormalizer:
    def normalize_batch(self, batch_result: CrawlBatchResult):
        # Step 6.1: جمع‌آوری همه آیتم‌ها
        all_items = collect_all_items(batch_result)
        
        # Step 6.2: حذف تکراری‌ها
        unique_items = remove_duplicates(all_items)
        
        # Step 6.3: نرمال‌سازی هر آیتم
        normalized_items = []
        for item in unique_items:
            normalized = self._normalize_item(item)
            normalized_items.append(normalized)
        
        # Step 6.4: مرتب‌سازی بر اساس کیفیت
        normalized_items.sort(key=lambda x: (
            x['confidence_score'],
            x['completeness_score']
        ), reverse=True)
```

### محاسبه امتیاز کامل‌بودن (Completeness Score)

```python
def _calculate_completeness(self, item: CrawledItem) -> float:
    score = 0.0
    max_score = 10.0
    
    # فیلدهای اجباری
    if item.title: score += 1.0      # 10%
    if item.url: score += 1.0        # 10%
    if item.price or item.price_text: score += 1.5  # 15%
    
    # فیلدهای مهم
    if item.location: score += 1.0   # 10%
    if item.images: score += 1.0      # 10%
    if item.description: score += 0.5  # 5%
    
    # فیلدهای اضافی
    if item.city: score += 0.5        # 5%
    if item.district: score += 0.5    # 5%
    if item.properties: score += 1.0  # 10%
    
    return min(score / max_score, 1.0)
```

### نتایج نرمال‌سازی

```json
{
  "normalization_stats": {
    "total_items_before": 302,
    "duplicates_removed": 12,
    "total_items_after": 290,
    "normalization_time": 0.45
  },
  "quality_distribution": {
    "high_quality": 245,
    "medium_quality": 38,
    "low_quality": 7
  }
}
```

---

## 📊 نتایج نهایی

### ساختار JSON کامل (100 آیتم از Torob)

```json
{
  "success": true,
  "total_items": 100,
  "items": [
    {
      "item_id": "torob_123456",
      "source_site": "torob",
      "title": "گوشی موبایل سامسونگ Galaxy S23 Ultra 256GB",
      "description": "گوشی سامسونگ گلکسی S23 اولترا با حافظه 256 گیگابایت، دوربین 200 مگاپیکسل، پردازنده Snapdragon 8 Gen 2",
      "url": "https://torob.com/product/123456",
      "price": 55.5,
      "price_text": "55,500,000 تومان",
      "price_type": "نقدی",
      "images": [
        "https://torob.com/images/product-123456-1.jpg",
        "https://torob.com/images/product-123456-2.jpg",
        "https://torob.com/images/product-123456-3.jpg"
      ],
      "thumbnail": "https://torob.com/images/product-123456-thumb.jpg",
      "properties": {
        "product_type": "electronics",
        "category": "گوشی موبایل",
        "brand": "Samsung",
        "model": "Galaxy S23 Ultra",
        "storage": "256GB",
        "ram": "12GB",
        "color": "Black",
        "screen_size": "6.8 اینچ",
        "camera": "200MP",
        "battery": "5000mAh",
        "os": "Android 13",
        "warranty": "12 ماه",
        "seller": "فروشگاه تکنولایف",
        "seller_rating": 4.8,
        "raw_data": {
          "original_html_snippet": "...",
          "extraction_method": "css_selectors",
          "extraction_timestamp": "2024-11-15T10:35:23"
        }
      },
      "crawled_at": "2024-11-15T10:35:23.456789",
      "goal_id": 3,
      "search_query": {
        "site": "torob",
        "filters": {
          "product_name": "گوشی موبایل",
          "price_max": 60,
          "price_min": 40
        },
        "goal_id": 3
      },
      "confidence_score": 0.92,
      "completeness_score": 0.95
    }
    // ... 99 آیتم دیگر
  ],
  "sources": ["torob"],
  "timestamp": "2024-11-15T10:36:00.123456",
  "metadata": {
    "normalization_applied": true,
    "duplicates_removed": 0,
    "execution_time": 12.45,
    "crawler_version": "1.0.0",
    "processing_steps": [
      "entity_extraction",
      "intent_classification",
      "query_generation",
      "crawling",
      "normalization"
    ]
  }
}
```

### آمار کلی نتایج

| معیار | مقدار |
|-------|-------|
| کل آیتم‌های یافت شده | 302 |
| آیتم‌های نرمال‌سازی شده | 290 |
| آیتم‌های حذف شده (تکراری) | 12 |
| زمان کل پردازش | 94.34 ثانیه |
| میانگین confidence score | 0.87 |
| میانگین completeness score | 0.91 |
| سایت‌های جستجو شده | 5 |
| اهداف جستجو | 3 |

---

## 📈 نمودار جریان کامل

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT (287 characters)                  │
│  "سلام من 600 میلیون نقد دارم و می‌توانم 200 میلیون هم        │
│   وام بگیرم تا 2 ماه آینده به دستم برسد. می‌خواهم بررسی کنم   │
│   با این مبلغ خانه در تهران اکباتان رهن کنم..."                │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ChatbotEngine.process_message()              │
│  - دریافت پیام                                                   │
│  - مدیریت session                                                │
│  - استخراج context                                               │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NLUProcessor.process()                      │
│  Step 1: EntityExtractor.extract_all_entities()                │
│    ├─ استخراج موجودیت‌های پولی: [600M, 200M, 15M]              │
│    ├─ استخراج مکان‌ها: ["تهران", "اکباتان"]                   │
│    ├─ استخراج اطلاعات وام: {amount: 200M, months: 2}           │
│    └─ استخراج نوع جستجو: {type: "residential_rent"}            │
│                                                                 │
│  Step 2: IntentClassifier.classify()                           │
│    └─ Intent: SEARCH, Confidence: 0.92                         │
│                                                                 │
│  Step 3: build_user_profile()                                   │
│    └─ UserProfile: {liquidity: 600M, loan: 200M, ...}         │
│                                                                 │
│  Step 4: build_search_goals()                                  │
│    └─ SearchGoals: [Goal1, Goal2, Goal3]                       │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    StructuredQuery Generated                    │
│  {                                                              │
│    "user_profile": {...},                                       │
│    "search_goals": [                                            │
│      {goal_id: 1, type: "residential_rent", location: "..."},  │
│      {goal_id: 2, type: "residential_rent", location: "..."},  │
│      {goal_id: 3, type: "vehicle", ...}                         │
│    ]                                                             │
│  }                                                               │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QueryGenerator.generate_queries()            │
│  - تولید 5 کوئری برای 5 سایت مختلف                              │
│  - تبدیل به فرمت قابل استفاده برای خزنده                        │
│  - اولویت‌بندی کوئری‌ها                                           │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CrawlerManager.crawl_batch()                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ DivarCrawler │  │SheypoorCrawler│  │ TorobCrawler  │        │
│  │   (45 items) │  │  (38 items)  │  │ (100 items)   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ BamaCrawler  │  │DigikalaCrawler│                            │
│  │  (52 items)  │  │  (67 items)   │                            │
│  └──────────────┘  └──────────────┘                            │
│  Total: 302 items, Time: 81.44s                                 │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DataNormalizer.normalize_batch()              │
│  - حذف تکراری‌ها: 12 آیتم                                        │
│  - نرمال‌سازی: 290 آیتم                                         │
│  - محاسبه کیفیت: confidence & completeness                      │
│  - مرتب‌سازی: بر اساس کیفیت                                     │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FINAL RESULTS (JSON)                         │
│  {                                                              │
│    "success": true,                                             │
│    "total_items": 290,                                          │
│    "items": [...],                                              │
│    "sources": ["divar", "sheypoor", "bama", "torob", "digikala"],│
│    "metadata": {...}                                            │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 جزئیات فنی کلاس‌ها

### کلاس ChatbotEngine

```python
class ChatbotEngine:
    """
    موتور اصلی چت‌بات
    
    Attributes:
        nlu_processor: پردازشگر زبان طبیعی
        query_generator: تولیدکننده کوئری
        conversation_history: تاریخچه مکالمات
    
    Methods:
        process_message(): پردازش پیام کاربر
        clear_session(): پاک کردن session
        get_conversation_summary(): دریافت خلاصه مکالمه
    """
```

### کلاس EntityExtractor

```python
class EntityExtractor:
    """
    استخراج‌کننده موجودیت‌ها
    
    Methods:
        extract_money_entities(): استخراج موجودیت‌های پولی
        extract_loan_info(): استخراج اطلاعات وام
        extract_location(): استخراج مکان‌ها
        extract_search_type(): استخراج نوع جستجو
        extract_all_entities(): استخراج همه موجودیت‌ها
        build_user_profile(): ساخت پروفایل کاربر
        build_search_goals(): ساخت اهداف جستجو
    """
```

### کلاس TorobCrawler

```python
class TorobCrawler(BaseCrawler):
    """
    خزنده سایت Torob
    
    Inherits:
        BaseCrawler: کلاس پایه خزنده
    
    Methods:
        build_search_url(): ساخت URL جستجو
        extract_items(): استخراج آیتم‌ها از HTML
        normalize_item(): نرمال‌سازی آیتم
    """
```

---

## 📝 خلاصه

این مستندات نشان می‌دهد که چگونه سیستم SEDE:

1. ✅ درخواست پیچیده کاربر را درک می‌کند
2. ✅ موجودیت‌های مهم را استخراج می‌کند
3. ✅ مقصود کاربر را تشخیص می‌دهد
4. ✅ کوئری‌های ساختاریافته تولید می‌کند
5. ✅ از چندین سایت به صورت موازی داده جمع‌آوری می‌کند
6. ✅ داده‌ها را نرمال‌سازی و یکپارچه می‌کند
7. ✅ نتایج با کیفیت را به صورت JSON برمی‌گرداند

تمام این فرآیند به صورت خودکار و با استفاده از معماری شی‌گرا و قابل گسترش انجام می‌شود.

</div>

