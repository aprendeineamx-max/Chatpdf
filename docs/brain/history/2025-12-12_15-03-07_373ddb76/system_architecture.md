# Arquitectura del Sistema "PDF Cortex" (Hydra Edition)

## Visión General
PDF Cortex es un sistema de **RAG (Retrieval-Augmented Generation)** avanzado diseñado para procesar, indexar y consultar documentos educativos masivos. La versión actual ("Hydra") implementa una arquitectura multi-llave para evitar límites de velocidad y maximizar la capacidad de procesamiento.

## Diagrama de Flujo de Datos
```mermaid
graph TD
    User[Usuario] -->|Pregunta + PDF| UI[Interfaz React (Vite)]
    UI -->|API Request| Backend[FastAPI Backend]
    
    subgraph "The Brain (Hydra)"
        Backend -->|Query| KeyManager[Gestor de Llaves]
        KeyManager -->|Round Robin| GeminiDriver[Custom Gemini Adapter]
        GeminiDriver -->|Gemini 2.0 Flash| GoogleAI[Google Cloud AI]
    end
    
    subgraph "Memory (Vector Store)"
        Backend -->|Embedding Search| VectorStore[Supabase / Local PGVector]
        VectorStore -->|Contexto Relevante| GeminiDriver
    end
    
    GoogleAI -->|Respuesta Generada| Backend
    Backend -->|Markdown Streams| UI
```

## Componentes Principales

### 1. Interfaz de Usuario (The Viz)
*   **Tecnología:** React 19 + Vite + TailwindCSS.
*   **Características:**
    *   Diseño oscuro "Cyberpunk/Premium".
    *   Visualización de Fuentes en tarjetas separadas.
    *   Renderizado Markdown completo.
*   **Función:** Captura la intención del usuario y presenta la respuesta de forma digerible.

### 2. Motor de IA (Hydra Engine)
*   **Tecnología:** Python + LlamaIndex + Google Generative AI (SDK).
*   **Innovación "Hydra":**
    *   **Multi-Tenancy de Llaves:** El sistema tiene cargadas 3 llaves de API distintas.
    *   **Rotación Round-Robin:** Cada consulta rota automáticamente a la siguiente llave libre.
    *   **Adaptador Personalizado:** Un driver escrito a medida (`CustomGemini`) que conecta LlamaIndex directamente con los modelos más nuevos de Google (`gemini-flash-latest`), saltándose limitaciones de librerías estándar.
*   **Modelo Actual:** `models/gemini-flash-latest` (Versión optimizada de Gemini 1.5/2.0 Flash sin bloqueos de cuota).

### 3. Memoria Vectorial (The Store)
*   **Tecnología:** Supabase (PostgreSQL con `pgvector`) o Almacenamiento Local (para desarrollo).
*   **Proceso:**
    1.  El PDF se divide en "chunks" (fragmentos de texto).
    2.  Se convierten a vectores numéricos usando `sentence-transformers/all-MiniLM-L6-v2`.
    3.  Cuando preguntas, el sistema busca los vectores más parecidos matemáticamente a tu pregunta.

## Por qué no usamos Snowflake (Aún)
El usuario mencionó "Snowflow" (Snowflake). Actualmente usamos **Supabase** porque es nativo de Postgres y perfecto para manejar vectores a esta escala. Snowflake es un Data Warehouse masivo excelente para analítica de petabytes, pero para una aplicación operativa de RAG ágil, Postgres/Supabase es la elección estándar de la industria por su velocidad en búsquedas vectoriales (latencia de milisegundos).

## Escalamiento Futuro
El sistema está diseñado para crecer. La arquitectura Hydra permite agregar 10, 20 o 50 llaves más simplemente actualizando el archivo de configuración, permitiendo procesar cientos de solicitudes por minuto sin fallar.
