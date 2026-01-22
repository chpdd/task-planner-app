from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import TypeAdapter

from typing import Iterable

from src.core.database import Base
from src.core.config import BaseSchema


class BaseCRUD[ORMModel: Base]:
    def __init__(self, orm_model: type[ORMModel]):
        self.orm_model = orm_model
        self.model_name = orm_model.__name__

    async def get(self, session: AsyncSession, obj_id: int) -> ORMModel | None:
        obj = await session.get(self.orm_model, obj_id)
        return obj

    async def get_by_name(self, session: AsyncSession, name: str) -> ORMModel | None:
        self.model_has_column_check("name")
        obj_stmt = select(self.orm_model).where(self.orm_model.name == name)
        obj = await session.scalar(obj_stmt)
        return obj

    async def list(self, session: AsyncSession) -> Iterable[ORMModel] | None:
        return (await session.scalars(select(self.orm_model))).all()

    async def create(self, session: AsyncSession, obj: ORMModel) -> None:
        session.add(obj)
        await session.flush()
        await session.refresh(obj)

    async def update(self, session: AsyncSession, obj: ORMModel, **kwargs) -> ORMModel:
        for key, val in kwargs.items():
            setattr(obj, key, val)
        await session.flush()
        await session.refresh(obj)
        return obj

    async def update_by_id(self, session: AsyncSession, obj_id: int, **kwargs) -> ORMModel:
        obj = await self.get(session, obj_id)
        return await self.update(session, obj, **kwargs)

    async def delete(self, session: AsyncSession, obj: ORMModel) -> None:
        await session.delete(obj)

    async def owner_all_delete(self, session: AsyncSession, owner_id: int) -> None:
        self.model_has_column_check("owner_id")
        stmt = delete(self.orm_model).where(self.orm_model.owner_id == owner_id)
        await session.execute(stmt)

    def model_has_column_check(self, column_name: str):
        if column_name not in self.orm_model.__mapper__.c:
            raise ValueError(f"Model {self.model_name} does not have column {column_name}")

class SchemaCRUD[ORMModel: Base, CreateSchema: BaseSchema, RetrieveSchema: BaseSchema](BaseCRUD):
    def __init__(self, orm_model: type[ORMModel], create_schema: type[CreateSchema],
                 retrieve_schema: type[RetrieveSchema]):
        self.retrieve_schema = retrieve_schema
        self.create_schema = create_schema
        super().__init__(orm_model)

    async def schema_get(self, session: AsyncSession, obj_id: int) -> RetrieveSchema | None:
        obj = await self.get(session, obj_id)
        return self.retrieve_schema.model_validate(obj)

    async def schema_get_by_name(self, session: AsyncSession, name: str) -> RetrieveSchema:
        obj = await self.get_by_name(session, name)
        return self.retrieve_schema.model_validate(obj)

    async def schema_owner_get(self, session: AsyncSession, obj_id: int, owner_id: int) -> RetrieveSchema | None:
        self.model_has_column_check("owner_id")
        obj = await self.get(session, obj_id)
        if obj is None or obj.owner_id != owner_id:
            return None
        return self.retrieve_schema.model_validate(obj)

    async def schema_list(self, session: AsyncSession) -> list[RetrieveSchema] | None:
        return [self.retrieve_schema.model_validate(obj) for obj in await self.list(session)]

    async def schema_owner_list(self, session: AsyncSession, owner_id: int) -> list[RetrieveSchema] | None:
        self.model_has_column_check("owner_id")
        stmt = select(self.orm_model).where(self.orm_model.owner_id == owner_id)
        objs = await session.scalars(stmt)
        type_adapter = TypeAdapter(list[self.retrieve_schema])
        return type_adapter.validate_python(objs)

    async def schema_create(self, session: AsyncSession, obj_schema: CreateSchema) -> RetrieveSchema:
        obj = self.orm_model(**obj_schema.model_dump())
        await self.create(session, obj)
        return self.retrieve_schema.model_validate(obj)

    async def schema_owner_create(self, session: AsyncSession, obj_schema: CreateSchema,
                                  owner_id: int) -> RetrieveSchema:
        obj = self.orm_model(**obj_schema.model_dump(), owner_id=owner_id)
        await self.create(session, obj)
        return self.retrieve_schema.model_validate(obj)

    async def schema_update(self, session: AsyncSession, obj: ORMModel,
                            update_obj_schema: CreateSchema) -> RetrieveSchema:
        obj = await self.update(session, **update_obj_schema.model_dump(exclude_unset=True))
        return self.retrieve_schema.model_validate(obj)

    async def schema_update_by_id(self, session: AsyncSession, obj_id,
                                  update_obj_schema: CreateSchema) -> RetrieveSchema:
        obj = await self.update_by_id(session, obj_id, **update_obj_schema.model_dump(exclude_unset=True))
        return self.retrieve_schema.model_validate(obj)
