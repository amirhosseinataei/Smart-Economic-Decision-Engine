"""
Script to generate sample JSON data with 100 items from Torob
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Sample data templates
brands = ["Samsung", "Apple", "Xiaomi", "OnePlus", "Honor", "Oppo", "Vivo", "Realme", "Motorola", "Nokia"]
models = {
    "Samsung": ["Galaxy S23 Ultra", "Galaxy S23", "Galaxy A54", "Galaxy Note 20", "Galaxy Z Fold"],
    "Apple": ["iPhone 14 Pro", "iPhone 14", "iPhone 13 Pro", "iPhone 12", "iPhone SE"],
    "Xiaomi": ["Redmi Note 12 Pro", "Mi 13", "Redmi 11", "POCO X5", "Mi 12"],
    "OnePlus": ["OnePlus 11", "OnePlus 10T", "OnePlus 9 Pro", "OnePlus Nord"],
    "Honor": ["Honor 90", "Honor 70", "Honor Magic5", "Honor X9a"],
    "Oppo": ["Find X5 Pro", "Reno 8", "A78", "A58"],
    "Vivo": ["X90 Pro", "V27", "Y78", "S17"],
    "Realme": ["GT 3", "11 Pro", "C55", "10 Pro"],
    "Motorola": ["Edge 40", "G82", "Moto G72"],
    "Nokia": ["G60", "X30", "G50"]
}

colors = ["Black", "White", "Blue", "Purple", "Green", "Gold", "Silver", "Red"]
storage_options = ["128GB", "256GB", "512GB"]
ram_options = ["6GB", "8GB", "12GB", "16GB"]
screen_sizes = ["6.1 اینچ", "6.4 اینچ", "6.7 اینچ", "6.8 اینچ"]

sellers = [
    "فروشگاه تکنولایف",
    "دیجی‌کالا",
    "اپل استور ایران",
    "فروشگاه ایران سرویس",
    "فروشگاه تکنوپلاس",
    "فروشگاه موبایل سنتر",
    "فروشگاه دیجی‌استایل",
    "فروشگاه موبایل لند"
]

def generate_item(item_id_base, index):
    """Generate a single item"""
    brand = random.choice(brands)
    model = random.choice(models[brand])
    storage = random.choice(storage_options)
    ram = random.choice(ram_options)
    color = random.choice(colors)
    screen_size = random.choice(screen_sizes)
    
    # Price between 40-60 million
    price = round(random.uniform(40, 60), 1)
    
    # Generate description
    description = f"گوشی {brand} {model} با حافظه {storage}، رم {ram}، رنگ {color}، نمایشگر {screen_size}"
    
    # Generate item ID
    item_id = f"torob_{item_id_base + index}"
    
    # Generate URL
    url = f"https://torob.com/product/{item_id_base + index}"
    
    # Generate images
    num_images = random.randint(1, 3)
    images = [f"https://torob.com/images/product-{item_id_base + index}-{i+1}.jpg" for i in range(num_images)]
    thumbnail = f"https://torob.com/images/product-{item_id_base + index}-thumb.jpg"
    
    # Generate crawled_at timestamp
    base_time = datetime.now()
    crawled_at = base_time + timedelta(seconds=index, microseconds=random.randint(0, 999999))
    
    # Generate seller rating
    seller_rating = round(random.uniform(4.3, 4.9), 1)
    
    # Generate confidence and completeness scores
    confidence_score = round(random.uniform(0.85, 0.95), 2)
    completeness_score = round(random.uniform(0.88, 0.97), 2)
    
    item = {
        "item_id": item_id,
        "source_site": "torob",
        "title": f"گوشی موبایل {brand} {model} {storage}",
        "description": description,
        "url": url,
        "price": price,
        "price_text": f"{int(price * 1000000):,} تومان",
        "price_type": "نقدی",
        "images": images,
        "thumbnail": thumbnail,
        "properties": {
            "product_type": "electronics",
            "category": "گوشی موبایل",
            "brand": brand,
            "model": model,
            "storage": storage,
            "ram": ram,
            "color": color,
            "screen_size": screen_size,
            "camera": f"{random.randint(48, 200)}MP",
            "battery": f"{random.randint(4000, 5000)}mAh",
            "os": random.choice(["Android 13", "iOS 16", "MIUI 14", "OxygenOS 13", "MagicOS 7.1"]),
            "warranty": "12 ماه",
            "seller": random.choice(sellers),
            "seller_rating": seller_rating,
            "in_stock": random.choice([True, True, True, False]),  # Mostly in stock
            "free_shipping": random.choice([True, False])
        },
        "crawled_at": crawled_at.isoformat(),
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
        "confidence_score": confidence_score,
        "completeness_score": completeness_score
    }
    
    return item

def generate_sample_data():
    """Generate complete sample data with 100 items"""
    item_id_base = 123456
    items = []
    
    for i in range(100):
        item = generate_item(item_id_base, i)
        items.append(item)
    
    # Calculate metadata
    total_price = sum(item["price"] for item in items)
    avg_price = total_price / len(items)
    avg_confidence = sum(item["confidence_score"] for item in items) / len(items)
    avg_completeness = sum(item["completeness_score"] for item in items) / len(items)
    
    result = {
        "success": True,
        "total_items": 100,
        "items": items,
        "sources": ["torob"],
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "normalization_applied": True,
            "duplicates_removed": 0,
            "execution_time": 12.45,
            "crawler_version": "1.0.0",
            "processing_steps": [
                "entity_extraction",
                "intent_classification",
                "query_generation",
                "crawling",
                "normalization"
            ],
            "query_filters": {
                "product_name": "گوشی موبایل",
                "price_max": 60,
                "price_min": 40
            },
            "total_pages_crawled": 10,
            "average_items_per_page": 10,
            "success_rate": 1.0,
            "statistics": {
                "average_price": round(avg_price, 2),
                "min_price": min(item["price"] for item in items),
                "max_price": max(item["price"] for item in items),
                "average_confidence": round(avg_confidence, 2),
                "average_completeness": round(avg_completeness, 2)
            }
        }
    }
    
    return result

if __name__ == "__main__":
    # Generate data
    data = generate_sample_data()
    
    # Save to file
    output_file = Path("data/sample_torob_results_100_items.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {data['total_items']} items")
    print(f"Saved to: {output_file}")
    print(f"Average price: {data['metadata']['statistics']['average_price']:.2f} million")
    print(f"Average confidence: {data['metadata']['statistics']['average_confidence']:.2f}")

