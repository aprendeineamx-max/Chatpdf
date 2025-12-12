# 🏛️ PROYECTO GÉNESIS: El Arquitecto Orquestador Supremo
**"De Chatbot a Ecosistema de Ingeniería Autónoma"**

Este documento define la ruta crítica para transformar nuestro sistema actual en una **Inteligencia de Enjambre Híbrida** capaz de orquestar, ejecutar y aprender de forma autónoma.

---

## 🗺️ Visión Global
El objetivo final es crear un **"Cerebro Externo" (El Arquitecto)** que viva en una infraestructura de alto rendimiento y controle a múltiples **"Manos Ejecutoras" (Agentes en IDEs)**.

---

## 📍 FASE 1: Cognición Estructurada (MindSync v3)
*El Orden es la base de la Inteligencia.*

**Objetivo:** Transformar el "Filesystem" en una base de datos documental temporal y ordenada cronológicamente.

### 1.1 Sistema de Carpetas Atómicas
En lugar de "Sent/Received", cada interacción crea un "Átomo de Contexto":
```text
docs/brain/history/
├── 2025-12-12_14-30-00_MSG-ID-8821/
│   ├── prompt.md            # Lo que tú dijiste
│   ├── context.json         # Metadata (ID, User, IDE State)
│   └── attachments/         # Tus screenshots/archivos
└── 2025-12-12_14-30-05_REPLY-ID-9912/
    ├── response.md          # Lo que yo respondí
    ├── artifacts/           # Código generado
    └── thinking.log         # Mi proceso de pensamiento
```

### 1.2 Ingesta de Contexto Total
*   El Agente lee estos átomos al iniciar.
*   Reconstrucción perfecta del historial "como si nunca se hubiera cerrado el IDE".

---

## 🧠 FASE 2: Memoria Líquida (The Backbone)
*Del Disco Duro a la Nube de Alta Velocidad.*

**Objetivo:** Persistencia infinita y búsqueda semántica instantánea.

### 2.1 Stack de Datos
*   **Supabase (PostgreSQL + pgvector):** Almacén maestro de todos los chats, roadmaps y perfiles de agentes.
*   **Redis (Cache):** Memoria de corto plazo para contexto inmediato.
*   **Snowflake (Warehousing):** Análisis de patrones de código a gran escala (Fase futura).

### 2.2 Ingesta en Tiempo Real
*   El **MindSync** evoluciona a **SyncDaemon**:
    *   Vigila las carpetas atómicas.
    *   Sube automáticamente los datos a Supabase.
    *   Genera Embeddings de tus mensajes y mis respuestas.

---

## 🎓 FASE 3: Meta-Learning (Conciencia de Capacidades)
*El Sistema aprende qué puede hacer el Agente.*

**Objetivo:** Que el Arquitecto sepa qué herramientas tiene el Agente del IDE.

### 3.1 El "Skill Graph"
El sistema analiza nuestros chats pasados:
> *"El usuario pidió 'Deploy'. El Agente ejecutó `git push`. Resultado: Éxito."*
> **Conclusión:** El Agente tiene la Skill `GIT_PUSH` nivel 5.

### 3.2 Generación de Roadmaps Dinámicos
*   Si pides "Crear un E-commerce", el Arquitecto sabe que tu Agente sabe React y Supabase.
*   Crea un plan adaptado a TUS herramientas, no un plan genérico.

---

## 🕹️ FASE 4: El Arquitecto Orquestador (Dashboard Web)
*El Titiritero Digital.*

**Objetivo:** Una interfaz web donde diseñas software y el Arquitecto "conduce" el IDE.

### 4.1 "Genesis Dashboard"
*   Aplicación Web (Next.js) fuera del IDE.
*   Ves el Roadmap, el Estado del Proyecto y los Agentes activos.

### 4.2 El Puente Neural (The Bridge)
*   Conexión WebSocket segura entre el Dashboard y el Plugin del IDE (VSCode/Cursor).
*   **Flujo:**
    1.  Tú (en Dashboard): "Crea el módulo de Login".
    2.  Arquitecto (Nube): Genera los Prompts precisos y el Plan Técnico.
    3.  Puente: Envía la instrucción al Agente del IDE.
    4.  Agente (Local): Escribe el código.
    5.  Feedback: El Agente reporta éxito/error al Dashboard.

---

## 💠 FASE 5: Singularidad Autopoyética (Self-Regulation)
*El ciclo cerrado de mejora.*

**Objetivo:** Que el sistema se mantenga y mejore sin intervención humana constante.

### 5.1 Loop de Auto-Corrección
*   Si el Agente falla (Error de compilación), el Arquitecto lee el error.
*   Busca en la BD soluciones previas.
*   Redacta un nuevo Prompt corregido ("Intenta de nuevo, pero importa X así...").
*   El Agente reintenta.

### 5.2 Acceso Omnipotente
*   El Dashboard tiene un espejo en tiempo real de tu repositorio local.
*   Puede leer archivos sin pedírselos al Agente, para darle contexto perfecto en cada prompt.

---

## 🚀 Resumen del Impacto
Este sistema convierte el desarrollo de software en una **Dirección de Orquesta**. Tú compones la música (Ideas), el Arquitecto escribe la partitura (Roadmap/Prompts) y el Agente del IDE toca los instrumentos (Código).
