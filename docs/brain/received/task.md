# Tareas: PDF Cortex System

## Fase 0: Documentación y Estrategia (Recurrente)
- [x] Generar Whitepaper Técnico Integral para Inversionistas (`project_whitepaper_es.md`)
- [x] Definir Arquitectura Multi-Llave y Roadmap de Crecimiento


## Fase 1: Infraestructura y Estructura Base <!-- id: 0 -->
- [x] Inicializar repositorio y estructura de directorios (`app/`, `data/`, `notebooks/`) <!-- id: 1 -->
- [ ] Configurar entorno virtual y gestión de dependencias (`uv`) <!-- id: 2 -->
- [x] Crear módulo `config.py` para gestión de API Keys (Groq, Gemini, Supabase) <!-- id: 3 -->

## Fase 2: Pipeline de Procesamiento (The Crusher) <!-- id: 4 -->
- [x] Implementar `PDFProcessor` class para dividir PDFs en imágenes (`pdf2image` / `PyMuPDF`) <!-- id: 5 -->
- [x] Implementar extracción de texto estructurado con `Marker` o `PyMuPDF` <!-- id: 6 -->
- [x] Crear sistema de almacenamiento local/nube para assets generados <!-- id: 7 -->

## Fase 3: Inteligencia y RAG (Brain) <!-- id: 8 -->
- [x] Configurar conexión con Supabase (PgVector) <!-- id: 9 --> (Mode: LOCAL por estabilidad)
- [x] Implementar inyección de documentos en LlamaIndex (`VectorStoreIndex`) <!-- id: 10 -->
- [x] Implementar Prompt Engineering (Español / Experto Educativo) <!-- id: 11 -->

## Fase 4: API & Endpoints <!-- id: 12 -->
- [x] Crear endpoint `POST /ingest` para recepción de PDFs via N8N <!-- id: 13 -->
- [x] Crear endpoint `POST /query` para consultas RAG estándar <!-- id: 14 -->
- [x] Crear endpoint `POST /page-query` para consultas específicas por página <!-- id: 15 -->

## Fase 5: Interfaz de Usuario (The Viz) <!-- id: 16 -->
- [x] Ingerir PDF Maestro del Usuario (`Nuestro Planeta la tierra`) <!-- id: 17 -->
- [x] Inicializar Proyecto Web (Vite + React + Tailwind) <!-- id: 18 -->
- [x] Componente de Chat (Markdown + Sources + Animations) <!-- id: 19 -->
- [x] Optimización de Retorno (Top-K=15 para mejor contexto) <!-- id: 20 -->

## Fase 6: Infraestructura Multi-Llave "Hydra" <!-- id: 21 -->
- [x] (P1) Implementar `KeyManager` y Rotación Round-Robin <!-- id: 22 -->
- [x] (P1) Configurar Retry con Failover Automático (Resuelto con Quota Hunter y Modelo Flash Latest) <!-- id: 23 -->
- [x] (P2) Implementar Ejecución Paralela ("Swarm") para lectura masiva <!-- id: 24 -->
    - [x] UI: Panel de Configuración "Hydra Control" (ControlPanel.tsx)
    - [x] Backend: Lógica `asyncio` Swarm (Query Sharding)
- [x] (P3) Persistencia de Llaves en Supabase <!-- id: 25 -->

## Fase 3: "Infinite Memory" - Persistencia y Alta Velocidad <!-- id: 30 -->
- [x] Base de Datos: Arquitectura Híbrida (SQLite/Postgres Fallback) <!-- id: 31 -->
- [x] Backend: Router de Chat y Guardado Asíncrono (ChatHistoryService) <!-- id: 32 -->
- [x] Frontend: Carga de Historial al iniciar (Sidebar.tsx) <!-- id: 33 -->
- [x] Cache: Redis para Contexto Inmediato (Hot Path) <!-- id: 34 -->

## Fase 4: Despliegue y Sincronización <!-- id: 40 -->
- [x] Git: Inicialización y Commit Local (v1.5) <!-- id: 41 -->
- [x] Git: Push a Remoto (aprendeineamx-max/Chatpdf) <!-- id: 42 -->

## Fase 5: Ecosistema de Plugins (Cortex Store) <!-- id: 50 -->
- [x] Core: Sistema de Registro "WordPress-Style" <!-- id: 51 -->
- [x] Plugin: Visualizador de Imágenes Nativo (Glassmorphism) <!-- id: 52 -->
- [x] Integration: Montaje de Capa de Plugins en App <!-- id: 53 -->

## Fase 6: MindSync (Puente Cognitivo) <!-- id: 60 -->
- [x] Tool: Motor de Sincronización Inteligente (Python) <!-- id: 61 -->
- [x] Logic: Estructura de Carpetas (Sent/Received) y Manifest.json <!-- id: 62 -->
- [x] Feature: "Watch Mode" para Sync en Tiempo Real <!-- id: 63 -->
