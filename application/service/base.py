from abc import ABC

# =====================BASE SERVICE WHICH OTHER SERVICE CAN INHERIT =============================================
class BaseService(ABC):
    def __init__(self, db_session):
        self._db_session = db_session

        # .