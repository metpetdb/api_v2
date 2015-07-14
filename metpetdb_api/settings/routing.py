class LegacyRouter(object):
    """
    A router to control all database operations on models in the
    legacy application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == 'legacy':
            return 'legacy'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to legacy.
        """
        if model._meta.app_label == 'legacy':
            return 'legacy'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if (obj1._meta.app_label == 'legacy' or
            obj2._meta.app_label == 'legacy'):
           return True
        return 'default'

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the auth app only appears in the 'legacy'
        database.
        """
        if app_label == 'legacy':
            return db == 'legacy'
        return 'default'
