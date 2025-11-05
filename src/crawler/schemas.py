"""
Schemas for crawler data structures
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ItemType(str, Enum):
    """Types of items"""
    RESIDENTIAL_RENT = "residential_rent"
    RESIDENTIAL_PURCHASE = "residential_purchase"
    VEHICLE = "vehicle"
    ELECTRONICS = "electronics"
    GENERAL = "general"


class CrawledItem(BaseModel):
    """Represents a crawled item from any website"""
    # Basic info
    item_id: str = Field(description="Unique item identifier")
    source_site: str = Field(description="Source website name")
    title: str = Field(description="Item title")
    description: Optional[str] = Field(default=None, description="Item description")
    url: str = Field(description="Item URL")
    
    # Pricing
    price: Optional[float] = Field(default=None, description="Price in Tomans")
    price_text: Optional[str] = Field(default=None, description="Price as text")
    price_type: Optional[str] = Field(default=None, description="Price type (نقدی, رهن, etc.)")
    
    # Location
    location: Optional[str] = Field(default=None, description="Location")
    city: Optional[str] = Field(default=None, description="City")
    district: Optional[str] = Field(default=None, description="District/Neighborhood")
    
    # Images
    images: List[str] = Field(default_factory=list, description="List of image URLs")
    thumbnail: Optional[str] = Field(default=None, description="Thumbnail image URL")
    
    # Additional properties
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    # Metadata
    crawled_at: datetime = Field(default_factory=datetime.now, description="Crawl timestamp")
    goal_id: Optional[int] = Field(default=None, description="Associated goal ID")
    search_query: Optional[Dict[str, Any]] = Field(default=None, description="Original search query")
    
    # Quality metrics
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in data quality")
    completeness_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Data completeness score")


class CrawlResult(BaseModel):
    """Result of a crawl operation"""
    success: bool = Field(description="Whether crawl was successful")
    site_name: str = Field(description="Website name")
    items: List[CrawledItem] = Field(default_factory=list, description="Crawled items")
    total_items: int = Field(default=0, description="Total items found")
    execution_time: float = Field(default=0.0, description="Execution time in seconds")
    errors: List[str] = Field(default_factory=list, description="List of errors if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CrawlBatchResult(BaseModel):
    """Result of batch crawl operation"""
    success: bool = Field(description="Overall success status")
    results: List[CrawlResult] = Field(default_factory=list, description="Results for each site")
    total_items: int = Field(default=0, description="Total items across all sites")
    execution_time: float = Field(default=0.0, description="Total execution time")
    timestamp: datetime = Field(default_factory=datetime.now, description="Batch timestamp")

