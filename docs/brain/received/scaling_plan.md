# Plan de Escalamiento: Arquitectura Multi-Llave "Hydra"

## Objetivo
Implementar un sistema de **Sinergia de APIs** que permita utilizar múltiples credenciales (API Keys) de forma simultánea e inteligente para:
1.  **Maximizar el Contexto:** Leer todo el libro (o grandes secciones) sin límites de tokens.
2.  **Eliminar Rate Limits:** Si una llave se satura, cambiar instantáneamente a otra (Failover).
3.  **Aumentar Velocidad:** Procesar consultas en paralelo (Swarm Processing).

---

## Estrategia Técnica

### 1. El Gestor de Llaves (`KeyManager`)
Un componente central (`app.core.key_manager`) responsable de:
*   **Key Vault:** Almacenar las llaves en memoria (y futuro DB).
*   **Rotation Logic:** Algoritmo *Round-Robin* o *Least-Used* para distribuir la carga.
*   **Health Checks:** Si una llave falla (429/403), marcarla como "Cooldown" temporalmente y sacarla de la rotación.

### 2. Ejecución "Enjambre" (Swarm Retrieval)
Para procesar 50+ páginas o el libro entero, una sola consulta lineal es ineficiente.
*   **Split & Conquer:** Dividir la intención del usuario en sub-tareas.
    *   *Ejemplo:* "Analiza el libro" -> Key 1 lee caps 1-3, Key 2 lee caps 4-6, Key 3 lee caps 7-9.
*   **Parallel Execution:** Usar `asyncio.gather` para lanzar estas peticiones simultáneamente, cada una con una Key distinta.
*   **Synthesizer:** Un nodo final que toma las respuestas parciales y las une en una respuesta maestra.

### 3. Estimación de Capacidad
*   **Estándar Gemini Free:** Aprox 15 RPM (Requests Per Minute) o 1 millón de tokens/min.
*   **Cálculo:**
    *   1 Consulta RAG Profunda (50 págs) ≈ 30k tokens.
    *   Con 1 Key: ~30 consultas/min.
    *   Con 3 Keys: ~90 consultas/min (o 3 consultas ultra-masivas simultáneas).
    *   **Meta:** Para leer 300 páginas de golpe, necesitamos dividir el libro en bloques de ~50 págs. -> 6 bloques. Con 3 keys, hacemos 2 rondas de procesamiento paralelo. Tiempo estimado: <10 segundos.

---

## Roadmap de Implementación

### Fase 1: Integración Inmediata (Next Steps)
- [ ] **Secure Storage:** Guardar las 3 llaves en `.env`.
- [ ] **Key Rotator Class:** Crear `KeyManager` en `app/core/key_manager.py`.
- [ ] **Engine Update:** Modificar `RAGService` para pedir una llave activa al `KeyManager` antes de cada consulta.
- [ ] **Retry Decorator:** Envolver las llamadas LLM con un decorador que reintente automáticamente con otra llave si detecta un error.

### Fase 2: Paralelismo (The Swarm)
- [ ] **Multi-Instance LLM:** Permitir instanciar múltiples objetos `OpenAILike` conectados a distintas cuentas.
- [ ] **Orquestador de Consultas:** Lógica para dividir una pregunta compleja en "Shards" y asignarlas a los LLMs disponibles.

### Fase 3: Infraestructura "Enterprise" (Futuro)
- [ ] **Base de Datos de Llaves:** Tabla `api_keys` en Supabase con columnas: `provider`, `key_encrypted`, `status`, `usage_count`, `last_error_at`.
- [ ] **Dashboard de Estado:** Ver en tiempo real qué llaves están activas, saturadas o muertas.

---

## Manejo de Errores y "Degradación Elegante"
La regla de oro solicitada: **Siempre entregar una respuesta**.
1.  **Escenario Ideal:** 3 Keys activas -> Leemos 100 páginas -> Respuesta Perfecta.
2.  **Escenario Carga Alta:** 2 Keys saturadas -> Leemos 30 páginas con la Key restante -> "Respuesta parcial (analizando 30% del libro)".
3.  **Escenario Crítico:** Todas saturadas -> Fallback a respuesta cacheada o mensaje de espera con estimación real.
