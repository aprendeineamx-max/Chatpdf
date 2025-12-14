
import sys
import os
import uuid
from datetime import datetime

# Add root to python path to import app modules
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, OrchestratorTask, init_db

def bootstrap_roadmap():
    print("🚀 Bootstrapping Active Roadmap...")
    
    # Ensure DB exists
    init_db()
    
    db = SessionLocal()
    
    tasks = [
        {
            "title": "Repo Share: Planificación y Requisitos",
            "description": "Definir requisitos de seguridad, tecnología de sincronización (WebSockets/SSH) y arquitectura de datos.",
            "status": "IN_PROGRESS",
            "assigned_agent": "system_architect",
            "priority": "HIGH"
        },
        {
            "title": "Repo Share: Implementación del Servidor",
            "description": "Configurar servidor Node.js/Python para WebSockets y API de recepción de archivos.",
            "status": "PENDING",
            "assigned_agent": "backend_dev",
            "priority": "HIGH"
        },
        {
            "title": "Repo Share: Implementación del Cliente",
            "description": "Desarrollar cliente de sincronización y panel de UI para visualización de diffs.",
            "status": "PENDING",
            "assigned_agent": "frontend_dev",
            "priority": "MEDIUM"
        }
    ]
    
    try:
        # Check if empty to avoid dupes? Nah, just insert for demo.
        for t in tasks:
            task = OrchestratorTask(
                id=str(uuid.uuid4()),
                title=t["title"],
                description=t["description"],
                status=t["status"],
                priority=t["priority"],
                assigned_agent=t["assigned_agent"],
                created_at=datetime.utcnow()
            )
            db.add(task)
        
        db.commit()
        print("✅ Roadmap Injected successfully.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    bootstrap_roadmap()
