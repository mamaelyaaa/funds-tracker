from abc import abstractmethod, ABC


class BaseOrmDTO[M, E](ABC):

    @staticmethod
    @abstractmethod
    def from_orm_to_entity(model: M) -> E: ...

    @staticmethod
    @abstractmethod
    def from_entity_to_orm(entity: E) -> M: ...
