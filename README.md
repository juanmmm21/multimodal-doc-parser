# Multimodal Document Parser

Este subproyecto forma parte de la infraestructura modular de Inteligencia Artificial ai-core-infra. Implementa un pipeline de parsing y extracción de documentos (Multimodal Document Parser) capaz de transformar archivos PDF e imágenes complejas con diseños variables en documentos estructurados en formato Markdown (GitHub Flavored Markdown).

Para este sistema decidí no utilizar dependencias complejas a nivel de sistema operativo como poppler (requerida comúnmente por pdf2image). En su lugar, utilicé PyMuPDF (fitz) para renderizar y manipular las páginas directamente en memoria, permitiendo un pipeline portable y de alto rendimiento.

---

## Arquitectura del Parser

El pipeline consta de tres fases fundamentales:

1. **Lectura y Renderización (PyMuPDF):** El parser recibe el archivo de entrada. Si es una imagen (PNG, JPG, JPEG), se lee directamente en bytes. Si es un archivo PDF, se abre de forma interactiva y cada página es renderizada en memoria como una imagen PNG de alta resolución (utilizando un factor de zoom de 2.0x, equivalente a ~150 DPI) para asegurar que el texto pequeño y las tablas se capturen con máxima nitidez. Adicionalmente, se extrae el texto digital nativo (si existe) de cada página para ser usado como respaldo (fallback).
2. **Abstracción de Backends (ParserBackend):** Se define una interfaz abstracta que permite alternar la estrategia de procesamiento de cada página:
   - **LocalExtractBackend (Local):** Extractor gratuito y local que procesa el texto digital nativo organizándolo en párrafos y cabeceras estructuradas de forma inmediata.
   - **VLMParserBackend (API de Visión):** Envía la imagen renderizada de la página a un Modelo de Lenguaje de Visión (VLM) como Google Gemini (gemini-2.5-flash) o GPT-4o de OpenAI. El modelo transcribe el diseño visual, convirtiendo tablas impresas a formato Markdown GFM e insertando explicaciones en cursiva que describen detalladamente el contenido de las imágenes o gráficas presentes.
3. **Consolidación de Contenido:** Se unifican las transcripciones estructuradas de todas las páginas en un documento Markdown estructurado único y se escribe en disco.

---

## Tecnologías Utilizadas

- **Python 3.10+** (Implementación tipada y modular).
- **PyMuPDF (fitz):** Para manipulación, extracción de metadatos de PDF y renderizado ultrarrápido en memoria de páginas de documentos.
- **Pillow (PIL):** Para el tratamiento y validación de las imágenes enviadas al VLM.
- **Google GenAI SDK & OpenAI SDK:** Integraciones para el análisis de visión multimodal con modelos de última generación.

---

## Instalación y Uso

### 1. Clonar e Inicializar
Clona este repositorio en tu máquina local y accede al directorio del proyecto:
```bash
git clone https://github.com/juanmmm21/multimodal-doc-parser.git
cd multimodal-doc-parser
```

### 2. Instalar Dependencias
Se recomienda el uso de un entorno virtual de Python. Instala los requisitos mediante pip:
```bash
pip install -r requirements.txt
```

### 3. Configuración de API Keys (Opcional)
Para habilitar el backend de visión VLM real utilizando Gemini, debes configurar tu variable de entorno en tu terminal antes de correr la demo:
```bash
export GEMINI_API_KEY="tu-clave-de-api-de-google-genai"
```
Si deseas probar con el backend de OpenAI, puedes configurar:
```bash
export OPENAI_API_KEY="tu-clave-de-api-de-openai"
```
Si no configuras ninguna clave de API, el sistema es resiliente y caerá automáticamente de forma segura al extractor local, reportando la advertencia.

### 4. Ejecutar Ejemplo de Demostración
El archivo `example.py` crea de forma programática un documento PDF digital de prueba y lo procesa con ambos backends (Local y VLM Fallback), exportando el Markdown resultante en `output_report.md`:
```bash
python3 example.py
```

### 5. Ejecutar Pruebas Unitarias
Ejecuta el conjunto de tests automáticos que validan la conversión y la resiliencia ante errores de API:
```bash
python3 -m unittest test_parser.py
```

---

## Conexión con el Ecosistema ai-core-infra

El multimodal-doc-parser cumple una función estructuradora en la ingesta:
- Los documentos transformados a Markdown estructurado alimentarán directamente al [semantic-chunking-engine](https://github.com/juanmmm21/semantic-chunking-engine) para fragmentar la información preservando los bloques temáticos.
- El tokenizador de [bpe-tokenizer-from-scratch](https://github.com/juanmmm21/bpe-tokenizer-from-scratch) es utilizado para calcular y calibrar la cantidad de tokens finales.
- Los fragmentos limpios resultantes de las tablas y textos estructurados por este parser se guardarán en la base de datos [nano-vector-db](https://github.com/juanmmm21/nano-vector-db) para habilitar capacidades de RAG híbrido y visual en la aplicación final [nexus-second-brain](https://github.com/juanmmm21/nexus-second-brain).
