from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

def validate_price(price_str: str) -> str:
    """Validate and normalize price string.
    
    Args:
        price_str: Price as string (e.g., "10.99", "5", "12.5")
    
    Returns:
        Normalized price string with exactly 2 decimal places
        
    Raises:
        ValueError: If price is invalid
    """
    try:
        # Convert to Decimal for exact decimal arithmetic
        price = Decimal(price_str)
        if price < 0:
            raise ValueError("Price cannot be negative")
        # Normalize to 2 decimal places
        return str(price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    except (ValueError, InvalidOperation):
        raise ValueError(f"Invalid price format: {price_str}")

@dataclass
class Item:
    shortDescription: str
    price: str
    
    def __post_init__(self):
        if not self.shortDescription:
            raise ValueError("Item description cannot be empty")
        self.shortDescription = self.shortDescription.strip()
        
        self.price = validate_price(self.price)

@dataclass
class Receipt:
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: List[Item] = field(default_factory=list)
    total: str = "0.00"
    
    def __post_init__(self):
        if not self.retailer or not self.retailer.strip():
            raise ValueError("Retailer name cannot be empty")
        self.retailer = self.retailer.strip()
        
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(self.purchaseDate, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "Invalid date format. Use YYYY-MM-DD"
                f" (got: {self.purchaseDate})"
            )
            
        # Validate time format (HH:MM)
        try:
            hour, minute = map(int, self.purchaseTime.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError()
        except Exception:
            raise ValueError(
                "Invalid time format. Use HH:MM (24-hour)"
                f" (got: {self.purchaseTime})"
            )
            
        if isinstance(self.items, list):
            try:
                self.items = [
                    item if isinstance(item, Item) else Item(**item)
                    for item in self.items
                ]
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid item data: {str(e)}")
                
        self.total = validate_price(self.total)
        
        # Optional: Verify total matches sum of items
        items_total = sum(Decimal(item.price) for item in self.items)
        receipt_total = Decimal(self.total)
        if items_total != receipt_total:
            print(f"Warning: Total ({receipt_total}) doesn't match"
                  f" sum of items ({items_total})")
    
    @property
    def purchase_datetime(self) -> datetime:
        """Get combined date and time as datetime object."""
        return datetime.strptime(
            f"{self.purchaseDate} {self.purchaseTime}",
            "%Y-%m-%d %H:%M"
        )
