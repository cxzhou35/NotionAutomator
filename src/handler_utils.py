from typing import Dict, Any, List
from .base_utils import DotDict
from .processor_utils import ProcessorFactory, PropertyProcessor


class DatabaseHandler:
    """Base database handler that uses property processors."""

    def __init__(self, processor_config: Dict[str, Any]):
        """
        Initialize with processor configuration.

        Args:
            processor_config: Dict with processor type and settings
                Example: {
                    'type': 'sum',
                    'properties': ['price', 'quantity'],
                    'options': {'separator': ', '}  # optional
                }
        """
        self.processor_type = processor_config['type']
        self.target_properties = processor_config['properties']
        self.options = processor_config.get('options', {})

        self.processor: PropertyProcessor = ProcessorFactory.create_processor(
            self.processor_type, **self.options
        )

    def process_data(self, queried_results: Dict[str, DotDict]) -> Dict[str, Any]:
        """Process the queried results and return formatted properties for Notion."""
        calculated_props = self.processor.calculate_properties(
            queried_results, self.target_properties
        )
        return self.processor.format_for_notion(calculated_props)


class PCBuildHandler(DatabaseHandler):
    """Handler for PC build databases - sums prices and counts components."""

    def __init__(self):
        super().__init__({
            'type': 'sum',
            'properties': ['价格', '预算分配']  # Can be configured
        })


class InventoryHandler(DatabaseHandler):
    """Handler for inventory databases - counts items and sums quantities."""

    def __init__(self):
        super().__init__({
            'type': 'sum',
            'properties': ['quantity', 'total_value']
        })


class ProjectHandler(DatabaseHandler):
    """Handler for project databases - counts tasks and calculates averages."""

    def __init__(self):
        super().__init__({
            'type': 'count',
            'properties': ['tasks', 'completed_tasks']
        })


class ResearchHandler(DatabaseHandler):
    """Handler for research databases - concatenates authors and counts papers."""

    def __init__(self):
        super().__init__({
            'type': 'concat',
            'properties': ['authors'],
            'options': {'separator': '; '}
        })


class MultiProcessorHandler:
    """Handler that can use multiple processors for different property groups."""

    def __init__(self, processor_configs: List[Dict[str, Any]]):
        """
        Initialize with multiple processor configurations.

        Args:
            processor_configs: List of processor configs
                Example: [
                    {'type': 'sum', 'properties': ['price']},
                    {'type': 'count', 'properties': ['items']},
                    {'type': 'concat', 'properties': ['tags'], 'options': {'separator': ', '}}
                ]
        """
        self.handlers = []
        for config in processor_configs:
            self.handlers.append(DatabaseHandler(config))

    def process_data(self, queried_results: Dict[str, DotDict]) -> Dict[str, Any]:
        """Process data using multiple processors and merge results."""
        merged_results = {}

        for handler in self.handlers:
            results = handler.process_data(queried_results)
            merged_results.update(results)

        return merged_results

# define the available handlers
_HANDLERS = {
    'pc_build': PCBuildHandler,
    'inventory': InventoryHandler,
    'project': ProjectHandler,
    'research': ResearchHandler,
}

class HandlerFactory:
    """Factory for creating database handlers."""


    @classmethod
    def create_handler(cls, handler_type: str) -> DatabaseHandler:
        """Create a handler instance."""
        if handler_type not in _HANDLERS:
            raise ValueError(f"Unknown handler type: {handler_type}")

        handler_class = _HANDLERS[handler_type]
        return handler_class()

    @classmethod
    def create_custom_handler(cls, processor_config: Dict[str, Any]) -> DatabaseHandler:
        """Create a custom handler with specific processor config."""
        return DatabaseHandler(processor_config)

    @classmethod
    def create_multi_handler(cls, processor_configs: List[Dict[str, Any]]) -> MultiProcessorHandler:
        """Create a multi-processor handler."""
        return MultiProcessorHandler(processor_configs)

    @classmethod
    def get_available_handlers(cls) -> List[str]:
        """Get list of available handler types."""
        return list(_HANDLERS.keys())
