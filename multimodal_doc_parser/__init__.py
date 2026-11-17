"""PDF/image document parser with a local extractor and pluggable VLM backends."""

from .backend import ParserBackend, LocalExtractBackend, VLMParserBackend
from .parser import MultimodalDocParser

__version__ = "0.1.0"

__all__ = ['ParserBackend', 'LocalExtractBackend', 'VLMParserBackend', 'MultimodalDocParser']
