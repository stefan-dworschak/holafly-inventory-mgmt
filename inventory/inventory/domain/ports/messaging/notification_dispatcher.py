from typing import List, Protocol


class NotificationDispatcher(Protocol):
    def dispatch_low_stock_notification(sku: str, quantity: int):
        """ Sends a low stock notification to the Procurement System that stock for
        a specific SKU is low and needs to be restocked """
        pass

