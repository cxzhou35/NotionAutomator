from decimal import Decimal
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .base_utils import DotDict


class PropertyProcessor(ABC):
    """Base class for property processors."""

    @abstractmethod
    def calculate_properties(self, queried_results: Dict[str, DotDict], target_props: List[str]) -> DotDict:
        """Calculate target properties from queried results."""
        pass

    @abstractmethod
    def format_for_notion(self, calculated_props: DotDict) -> Dict[str, Any]:
        """Format calculated properties for Notion API."""
        pass


class NumericSumProcessor(PropertyProcessor):
    """Processor for summing numeric properties (e.g., prices, quantities)."""

    def calculate_properties(self, queried_results: Dict[str, DotDict], target_props: List[str]) -> DotDict:
        """Sum all numeric properties."""
        target_meta = DotDict()

        for prop_name in target_props:
            target_meta[prop_name] = Decimal('0')
            for obj_id, obj_meta in queried_results.items():
                if obj_meta[prop_name] is not None:
                    target_meta[prop_name] += Decimal(str(obj_meta[prop_name]))

        return target_meta

    def format_for_notion(self, calculated_props: DotDict) -> Dict[str, Any]:
        """Format numeric properties for Notion API."""
        formatted = {}
        for prop_name, value in calculated_props.items():
            formatted[prop_name] = {
                "number": float(value)
            }
        return formatted


class NumericAverageProcessor(PropertyProcessor):
    """Processor for calculating average of numeric properties."""

    def calculate_properties(self, queried_results: Dict[str, DotDict], target_props: List[str]) -> DotDict:
        """Calculate average of numeric properties."""
        target_meta = DotDict()

        for prop_name in target_props:
            total = Decimal('0')
            count = 0

            for obj_id, obj_meta in queried_results.items():
                if obj_meta[prop_name] is not None:
                    total += Decimal(str(obj_meta[prop_name]))
                    count += 1

            target_meta[prop_name] = total / count if count > 0 else Decimal('0')

        return target_meta

    def format_for_notion(self, calculated_props: DotDict) -> Dict[str, Any]:
        """Format numeric properties for Notion API."""
        formatted = {}
        for prop_name, value in calculated_props.items():
            formatted[prop_name] = {
                "number": float(value)
            }
        return formatted


class CountProcessor(PropertyProcessor):
    """Processor for counting non-empty properties."""

    def calculate_properties(self, queried_results: Dict[str, DotDict], target_props: List[str]) -> DotDict:
        """Count non-empty properties."""
        target_meta = DotDict()

        for prop_name in target_props:
            count = 0
            for obj_id, obj_meta in queried_results.items():
                if obj_meta[prop_name] is not None and obj_meta[prop_name] != "":
                    count += 1

            target_meta[prop_name] = count

        return target_meta

    def format_for_notion(self, calculated_props: DotDict) -> Dict[str, Any]:
        """Format count properties for Notion API."""
        formatted = {}
        for prop_name, value in calculated_props.items():
            formatted[prop_name] = {
                "number": int(value)
            }
        return formatted


class TextConcatenationProcessor(PropertyProcessor):
    """Processor for concatenating text properties."""

    def __init__(self, separator: str = ", "):
        self.separator = separator

    def calculate_properties(self, queried_results: Dict[str, DotDict], target_props: List[str]) -> DotDict:
        """Concatenate text properties."""
        target_meta = DotDict()

        for prop_name in target_props:
            texts = []
            for obj_id, obj_meta in queried_results.items():
                if obj_meta[prop_name] and str(obj_meta[prop_name]).strip():
                    texts.append(str(obj_meta[prop_name]))

            target_meta[prop_name] = self.separator.join(texts)

        return target_meta

    def format_for_notion(self, calculated_props: DotDict) -> Dict[str, Any]:
        """Format text properties for Notion API."""
        formatted = {}
        for prop_name, value in calculated_props.items():
            formatted[prop_name] = {
                "rich_text": [{"text": {"content": str(value)}}]
            }
        return formatted


class SelectCollectionProcessor(PropertyProcessor):
    """Processor for collecting unique select/multi-select values."""

    def calculate_properties(self, queried_results: Dict[str, DotDict], target_props: List[str]) -> DotDict:
        """Collect unique select values."""
        target_meta = DotDict()

        for prop_name in target_props:
            unique_values = set()
            for obj_id, obj_meta in queried_results.items():
                if obj_meta[prop_name]:
                    if isinstance(obj_meta[prop_name], list):
                        # Multi-select
                        for item in obj_meta[prop_name]:
                            if isinstance(item, dict) and 'name' in item:
                                unique_values.add(item['name'])
                            else:
                                unique_values.add(str(item))
                    elif isinstance(obj_meta[prop_name], dict) and 'name' in obj_meta[prop_name]:
                        # Single select
                        unique_values.add(obj_meta[prop_name]['name'])
                    else:
                        unique_values.add(str(obj_meta[prop_name]))

            target_meta[prop_name] = list(unique_values)

        return target_meta

    def format_for_notion(self, calculated_props: DotDict) -> Dict[str, Any]:
        """Format select properties for Notion API."""
        formatted = {}
        for prop_name, values in calculated_props.items():
            formatted[prop_name] = {
                "multi_select": [{"name": value} for value in values]
            }
        return formatted


class ProcessorFactory:
    """Factory for creating property processors."""

    _processors = {
        'sum': NumericSumProcessor,
        'average': NumericAverageProcessor,
        'count': CountProcessor,
        'concat': TextConcatenationProcessor,
        'collect': SelectCollectionProcessor,
    }

    @classmethod
    def create_processor(cls, processor_type: str, **kwargs) -> PropertyProcessor:
        """Create a processor instance."""
        if processor_type not in cls._processors:
            raise ValueError(f"Unknown processor type: {processor_type}")

        processor_class = cls._processors[processor_type]
        return processor_class(**kwargs)

    @classmethod
    def get_available_processors(cls) -> List[str]:
        """Get list of available processor types."""
        return list(cls._processors.keys())
