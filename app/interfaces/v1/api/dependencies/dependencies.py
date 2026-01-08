from app.domain.uow.unit_of_work import UnitOfWork
from app.infrastructure.database.uow import SqlAlchemyUnitOfWork


def get_uow() -> UnitOfWork:
    return SqlAlchemyUnitOfWork()
