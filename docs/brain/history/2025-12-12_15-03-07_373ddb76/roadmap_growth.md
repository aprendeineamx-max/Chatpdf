# Roadmap & Estrategia de Crecimiento Exponencial: PDF Cortex

Este documento detalla la evolución de "PDF Cortex" de una herramienta de procesamiento a un ecosistema de inteligencia artificial líder.

## Fase 1: Los Cimientos de Titanio (Semana 1)
**Objetivo**: Procesamiento perfecto y "Memory Palace" (Palacio de la Memoria).
*   [ ] **Pipeline de Ingesta**: Lograr que un PDF se convierta en assets limpios (imágenes HD + Markdown) sin errores.
*   [ ] **Vectorización Híbrida**: Implementar LlamaIndex con índices de Árbol (para resúmenes) y Vectoriales (para búsqueda específica).
*   [ ] **API Robusta**: Endpoints FastAPI listos para producción con manejo de errores y autenticación básica.

## Fase 2: Conectividad Neural (Semana 2)
**Objetivo**: Integración fluida con el ecosistema NO-CODE (N8N).
*   [ ] **Conector N8N**: Crear un "Workflow Template" en JSON para importar en N8N que se conecte a nuestra API.
*   [ ] **Webhooks Activos**: Que el sistema "avise" a N8N cuando un PDF terminó de leerse (Evitar polling).
*   [ ] **Memoria Conversacional**: Implementar hilos de conversación (ThreadID) para que el chat tenga memoria de preguntas anteriores.

## Fase 3: La Visión de Dios (Multimodalidad) (Semana 3-4)
**Objetivo**: Que la IA no solo lea texto, sino que *entienda* diagramas y fotos.
*   [ ] **Vision RAG**: Usar Gemini 2.0 Flash o Llama 3.2 Vision para generar descripciones textuales de las imágenes extraídas en la Fase 1 e indexarlas.
*   [ ] **Query Visual**: Poder preguntar "¿Qué significa el gráfico de la página 12?" y que la IA "mire" la imagen `page_12.png`.

## Fase 4: Agentes Autónomos (Deep Research) (Mes 2)
**Objetivo**: Transformar el sistema de pasivo (esperar preguntas) a activo (generar insights).
*   [ ] **Agente Investigador**: Un sub-agente que, al cargar un PDF, automáticamente genere un "Reporte de Anomalías" o "Resumen Ejecutivo" sin que nadie lo pida.
*   [ ] **Graph RAG**: Construir un grafo de conocimiento (Knowledge Graph) para conectar conceptos entre múltiples PDFs (ej: conectar "Contrato A" con "Factura B").

## Estrategia de Infraestructura y Optimización
Para lograr eficiencia máxima y bajos costos:
1.  **Storage**: Usar **Supabase Storage** (compatible S3) para las imágenes. Es escalable y barato.
2.  **Base de Datos**: **Supabase PostgreSQL**. Es el "gold standard" para pgvector.
3.  **Computación (Worker)**:
    *   Para OCR pesado/GPU: Usar **Modal.com** (Serverless GPU). Solo pagas por los segundos que procesas el PDF.
    *   Para API ligera: VPS (Ubuntu) o Docker container estándar.
4.  **Cache**: **Redis**. Para guardar respuestas frecuentes y no gastar tokens de LLM en preguntas repetidas.

## Recomendación de Stack "Best in Class"
*   **LLM Orchestrator**: LlamaIndex (Mejor manejo de datos estructurados que LangChain).
*   **Database**: Supabase.
*   **Vision Model**: Gemini 2.0 Flash (Rápido, barato, ventana de contexto enorme).
*   **Inference**: Groq (Para respuestas de texto instantáneas).

## Fase 5: Futuro (Hydra Expansion)
- [ ] **Swarm Retrieval:** Procesamiento paralelo de múltiples documentos usando `asyncio` y múltiples llaves simultáneamente.
- [ ] **Autenticación de Usuarios:** Integración completa con Supabase Auth para perfiles privados.
- [ ] **Key Vault DB:** Migrar las llaves de `.env` a una tabla cifrada en Supabase para gestión dinámica desde un panel de admin.
- [ ] **Data Warehouse:** Integración con **Snowflake** para análisis de patrones de uso y big data de documentos procesados.
