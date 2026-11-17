"""Compatibilidad: el código vive en el paquete `multimodal_doc_parser`. Este módulo se
conserva para quien añade esta carpeta a `sys.path` e importa `parser`
directamente."""

from multimodal_doc_parser.parser import *  # noqa: F401,F403
from multimodal_doc_parser.parser import MultimodalDocParser  # noqa: F401
