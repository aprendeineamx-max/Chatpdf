# PDF Cortex

El sistema de inteligencia artificial documental más avanzado, diseñado para "atomizar" PDFs en conocimiento estructurado e interactuar vía API.

## Características
*   **Segmentación por Página**: Entiende exactamente qué contenido pertenece a qué página.
*   **Visión Multimodal**: No solo OCR, sino descripción de imágenes con Gemini 2.0.
*   **Integración N8N**: API First, diseñada para ser un cerebro remoto.
*   **Alta Fidelidad**: Conversión de PDF a Markdown estructurado + Imágenes HD.

## Estructura del Proyecto
*   `app/api`: Endpoints REST (FastAPI).
*   `app/core`: Configuración y secretos.
*   `app/services`: Lógica de negocio (Ingesta, RAG, LLM).
*   `data/`: Almacenamiento temporal de archivos procesados.

## Setup Inicial

1.  **Crear entorno virtual**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
2.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configurar variables**:
    Crea un archivo `.env` basado en `.env.example` y agrega tus API Keys.

4.  **Ejecutar**:
    ```bash
    uvicorn app.main:app --reload
    ```
