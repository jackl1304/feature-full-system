from abc import ABC, abstractmethod
from typing import List, Dict

class SourcePlugin(ABC):
    """
    Basis-Klasse für alle Fetcher-Plugins
    """
    @abstractmethod
    async def fetch(self) -> List[Dict]:
        """
        Muss eine Liste von Dicts zurückliefern mit keys:
        title, link, published, source
        """
        ...
