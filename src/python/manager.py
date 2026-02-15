import logging 

class AXC1DEventManager:
    """
    Docstring for AXC1DEventManager
    """
    def __init__(self, logger: logging.Logger):
        """
        Docstring for __init__
        
        :param self: Description
        :param logger: Description
        :type logger: logging.Logger
        """
        self.logger = logger
        self.listeners = {}

    def subscribe(self, event_name, callback):
        """
        Docstring for subscribe
        
        :param self: Description
        :param event_name: Description
        :param callback: Description
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def emit(self, event_name):
        """
        Docstring for emit
        
        :param self: Description
        :param event_name: Description
        """
        for callback in self.listeners.get(event_name, []):
            callback()