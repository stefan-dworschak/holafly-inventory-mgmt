from abc import ABC, abstractmethod


class NotificationDispatcher(ABC):
    @abstractmethod
    def dispatch_low_stock_notification(self, sku: str, quantity: int) -> None:
        """ Sends a low stock notification to the Procurement System that stock for
        a specific SKU is low and needs to be restocked """
