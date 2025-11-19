"""
Sistema de backup automático de SQLite a GitHub/S3
para mantener datos persistentes en despliegues efímeros.
"""
import os
import sqlite3
import shutil
from datetime import datetime
import base64
import requests

class BackupManager:
    """Gestiona backups de BD SQLite en servicios cloud."""
    
    def __init__(self, db_path='axs_v2.db'):
        self.db_path = db_path
        self.backup_methods = {
            'github': self._backup_to_github,
            'local': self._backup_to_local,
        }
    
    def _backup_to_local(self):
        """Backup local con timestamp."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'backups/axs_v2_backup_{timestamp}.db'
        os.makedirs('backups', exist_ok=True)
        shutil.copy2(self.db_path, backup_path)
        print(f"✅ Backup local: {backup_path}")
        return backup_path
    
    def _backup_to_github(self):
        """
        Backup a GitHub usando API.
        
        Requiere:
        - GITHUB_TOKEN (env var)
        - GITHUB_REPO (formato: owner/repo)
        """
        token = os.getenv('GITHUB_TOKEN')
        repo = os.getenv('GITHUB_REPO', 'B10sp4rt4n/Accesos-Residencial')
        
        if not token:
            print("⚠️ GITHUB_TOKEN no configurado")
            return None
        
        # Leer BD y convertir a base64
        with open(self.db_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode()
        
        # Nombre de archivo en GitHub
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = f'backups/axs_v2_backup_{timestamp}.db'
        
        # API GitHub para crear/actualizar archivo
        url = f'https://api.github.com/repos/{repo}/contents/{file_path}'
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'message': f'Auto-backup BD {timestamp}',
            'content': content,
            'branch': 'backups'  # Rama separada para backups
        }
        
        response = requests.put(url, json=data, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"✅ Backup a GitHub: {file_path}")
            return file_path
        else:
            print(f"❌ Error backup GitHub: {response.status_code}")
            return None
    
    def create_backup(self, method='local'):
        """
        Crea backup usando el método especificado.
        
        Args:
            method: 'local', 'github'
        """
        if method in self.backup_methods:
            return self.backup_methods[method]()
        else:
            print(f"⚠️ Método desconocido: {method}")
            return None
    
    def restore_latest(self, source='local'):
        """Restaura el backup más reciente."""
        if source == 'local':
            backups = sorted([f for f in os.listdir('backups') if f.endswith('.db')])
            if backups:
                latest = backups[-1]
                shutil.copy2(f'backups/{latest}', self.db_path)
                print(f"✅ Restaurado: {latest}")
                return True
        return False
    
    def auto_backup_on_change(self):
        """
        Detecta cambios en BD y crea backup automático.
        
        Uso en Streamlit:
            if st.button("Guardar"):
                # ... guardar datos ...
                BackupManager().auto_backup_on_change()
        """
        # Verificar si hay cambios
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sqlite_sequence")
        changes = cur.fetchone()[0] if cur.fetchone() else 0
        conn.close()
        
        if changes > 0:
            self.create_backup('local')
            
            # Si está en producción, backup a GitHub también
            if os.getenv('STREAMLIT_SHARING'):
                self.create_backup('github')


# Uso simple
def backup_database():
    """Función helper para backup rápido."""
    manager = BackupManager()
    manager.create_backup('local')
    
    # En producción también a GitHub
    if os.getenv('GITHUB_TOKEN'):
        manager.create_backup('github')


# Auto-backup al iniciar app (restaurar último backup)
def restore_on_startup():
    """
    Restaura BD desde backup si no existe o está vacía.
    
    Llamar al inicio de app.py:
        from app.database.backup_manager import restore_on_startup
        restore_on_startup()
    """
    db_path = 'axs_v2.db'
    
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        print("⚠️ BD no existe o está vacía. Restaurando backup...")
        manager = BackupManager()
        
        # Intentar restaurar desde GitHub primero
        # (implementar si es necesario)
        
        # Sino, desde local
        if manager.restore_latest('local'):
            print("✅ BD restaurada exitosamente")
        else:
            print("⚠️ No hay backups disponibles. Creando BD nueva...")
