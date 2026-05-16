from typing import List, Protocol


class EventService(Protocol):
    def trigger_log_stock_alert(sku: str):
        """ Triggers an event to inform the Procurement System that stock for
        a specific SKU is low and needs to be restocked """
        pass

