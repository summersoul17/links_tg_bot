import asyncio
import logging

from typing import List

from sqlalchemy import select, MetaData, text, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

from src.config import settings
from src.db.models import Link, Tag
from src.db.schemas import LinkSchema, TagSchema

logger = logging.getLogger(__name__)

async_engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def create_tables():
    async with async_engine.connect() as connection:
        await connection.run_sync(Link.metadata.create_all)
        stmt = text("""SELECT * FROM links;""")
        result = await connection.execute(stmt)
        await connection.commit()
        print([LinkSchema.model_validate(i) for i in result.scalars().all()])


async def drop_tables():
    async with async_engine.begin() as connection:
        await connection.run_sync(Link.metadata.drop_all)
        await connection.commit()


async def get_links(tag_id: int | None = None) -> List[dict]:
    async with async_session() as session:
        if tag_id:
            query = select(Link).where(Link.tag_id == tag_id)
        else:
            query = select(Link)
        links = await session.execute(query)
        links = links.scalars().all()
        return [LinkSchema.model_validate(link, from_attributes=True).model_dump() for link in links]


async def add_link(data: dict):
    async with async_session() as session:
        link = Link(**data)
        session.add(link)
        await session.commit()


async def add_tag(tag: str):
    print("Зашел в add_tag")
    async with async_session() as session:
        query = select(Tag).where(Tag.name == tag.lower())
        tags = await session.execute(query)
        result = [TagSchema.model_validate(i, from_attributes=True).model_dump() for i in tags.scalars().all()]
        print(f"Получил результат {result}")
        if not result:
            print("Результат пустой")
            tag_ = Tag(**{"name": tag.lower()})
            session.add(tag_)
            await session.flush()
            await session.commit()
            print(f"Добавил тег в базу. ID={tag_.id}")
            return tag_.id
        else:
            print(f"Результат не пустой. ID={result[0]['id']}")
            return result[0]["id"]


async def get_tags(tag_id: int | None = None) -> List[dict]:
    async with async_session() as session:
        if tag_id:
            query = select(Tag).where(Tag.id == tag_id)
        else:
            query = select(Tag)
        tags = await session.execute(query)
        return [TagSchema.model_validate(i, from_attributes=True).model_dump() for i in tags.scalars().all()]


async def update_link(link_id: int, description: str):
    async with async_session() as session:
        link = await session.get(Link, link_id)
        link.description = description
        await session.commit()


async def delete_link(link: dict):
    async with async_session() as session:
        query = delete(Link).where(Link.id == link['id'])
        await session.execute(query)
        await session.commit()
