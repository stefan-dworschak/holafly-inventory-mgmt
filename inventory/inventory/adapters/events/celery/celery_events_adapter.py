from inventory.domain.ports.events.events_service import EventsService

class CeleryEventsAdapter(EventsService):
    def trigger_log_stock_alert(self, sku: str):
        pass
