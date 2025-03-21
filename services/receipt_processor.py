import uuid
import math
from datetime import datetime
import logging
from models.receipt import Receipt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReceiptProcessor:

    _points_cache = {}
    
    def __init__(self):
        # stores processed receipts and their points
        # switched from list to dict for O(1) lookups
        self._receipts = {}

    def process_receipt(self, receipt: Receipt) -> str:
        """Process a receipt and return its ID.
        
        Returns UUID so we can track receipts across services.
        """
        id = str(uuid.uuid4())
        points, point_details = self._calc_receipt_points(receipt)
        
        self._receipts[id] = points
        
        logger.info(f"Receipt {id[:8]}... processed:")
        for detail in point_details:
            logger.info(f"  {detail}")
        
        return id

    def get_points(self, receipt_id: str) -> int:
        """Get points for a receipt. Raises ValueError if not found."""
        try:
            return self._receipts[receipt_id]
        except KeyError:
            raise ValueError(f"No receipt found with ID: {receipt_id}")

    def _calc_receipt_points(self, receipt: Receipt) -> tuple[int, list]:
        """Calculate points for a receipt based on the rules.
        
        Returns (total_points, breakdown_messages)
        """
        points = 0  # running total
        messages = []
        
        # rule 1 - retailer name
        alphanums = sum(1 for c in receipt.retailer if c.isalnum())
        points += alphanums
        messages.append(f"{alphanums} points - retailer name has {alphanums} alphanumeric chars")

        # rules 2 & 3 - round dollar and quarters
        total = float(receipt.total)
        if total.is_integer():
            points += 50
            messages.append("50 points - round dollar amount")
        if total % 0.25 == 0:  # check for multiples of 0.25
            points += 25
            messages.append("25 points - multiple of 0.25")

        # rule 4 - item pairs
        pair_points = (len(receipt.items) // 2) * 5  # integer division
        if pair_points:
            points += pair_points
            messages.append(f"{pair_points} points - {len(receipt.items)} items = {len(receipt.items)//2} pairs")

        # rule 5 - description length
        for item in receipt.items:
            desc = item.shortDescription.strip()
            # if len(desc) % 3 == 0:  # intentionally commented
            #     p = math.ceil(float(item.price) * 0.2)
            #     points += p
            #     messages.append(
            #         f"{p} points - '{desc}' len({len(desc)}) is mult of 3"
            #     )
            if len(desc) % 3 == 0:
                points += math.ceil(float(item.price) * 0.2)
                messages.append(
                    f"{math.ceil(float(item.price)*0.2)} points - '{desc}' len({len(desc)}) is mult of 3"
                )

        # rule 6 - odd day
        day = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d").day
        if day % 2:  # odd day
            points += 6
            messages.append(f"6 points - day {day} is odd")

        # rule 7 - time range (2-4 PM)
        time = datetime.strptime(receipt.purchaseTime, "%H:%M")
        if datetime.strptime("14:00", "%H:%M") <= time <= datetime.strptime("16:00", "%H:%M"):
            points += 10
            messages.append("10 points - purchased 2-4 PM")

        messages.append(f"Total: {points} points")
        return points, messages