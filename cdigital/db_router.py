from threading import local
from utils.database_selector import get_local_database_name  # você criará esse módulo também

_thread_local = local()

#def set_current_database(db_name):
#    _thread_local.db = db_name

def get_current_database():
    # Usa o nome do banco do arquivo .ini
    if not hasattr(_thread_local, 'db'):
        _thread_local.db = get_local_database_name()
    return _thread_local.db

class MultiTenantRouter:
    def db_for_read(self, model, **hints):
        return get_current_database()

    def db_for_write(self, model, **hints):
        return get_current_database()

    def allow_relation(self, obj1, obj2, **hints):
        db = get_current_database()
        return db == obj1._state.db == obj2._state.db

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'