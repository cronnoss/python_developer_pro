# Added
from domain.unit_of_work import UnitOfWork
from sqlalchemy.orm import Session

from .repositories import SqlAlchemyProductRepository, SqlAlchemyOrderRepository, SqlAlchemyCustomerRepository


class SqlAlchemyUnitOfWork(UnitOfWork):

    def __init__(self, session: Session):
        self.session = session
        self.product_repo = SqlAlchemyProductRepository(session)
        self.order_repo = SqlAlchemyOrderRepository(session)
        self.customer_repo = SqlAlchemyCustomerRepository(session)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            self.commit()
        else:
            self.rollback()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
