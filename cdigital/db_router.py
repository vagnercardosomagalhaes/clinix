from threading import local
from utils.database_selector import get_local_database_name

_thread_local = local()

def get_current_database():
    # Usa o nome do banco do arquivo .ini
    if not hasattr(_thread_local, 'db'):
        _thread_local.db = get_local_database_name()
    return _thread_local.db

class MultiTenantRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'cdigital':
            return 'default'
        return get_current_database()       

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'cdigital':
            return 'default'
        return get_current_database()

    def allow_relation(self, obj1, obj2, **hints):
        # Permite relação se ambos forem do mesmo banco
        if obj1._state.db == obj2._state.db:
            return True

        # Permite relação entre apps internos do Django
        if obj1._meta.app_label in ('auth', 'admin', 'contenttypes', 'sessions') or \
           obj2._meta.app_label in ('auth', 'admin', 'contenttypes', 'sessions'):
            return True

        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'