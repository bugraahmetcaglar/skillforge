class DatabaseRouter:
    """
    Database router for directing database operations to the appropriate database.
    This router directs read and write operations for the logging app to a MongoDB database,
    while all other operations go to the default database.
    """

    def db_for_read(self, model, **hints):
        """Reading from the logging database."""
        if model._meta.app_label == "logging" or model.__name__ == "LogEntry":
            return "mongodb"
        return "default"

    def db_for_write(self, model, **hints):
        """Writing to the logging database."""
        if model._meta.app_label == "logging" or model.__name__ == "LogEntry":
            return "mongodb"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app."""
        db_set = {"default", "mongodb"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        if app_label == "logging" or model_name == "logentry":
            return db == "mongodb"
        elif db == "mongodb":
            return False
        return db == "default"
