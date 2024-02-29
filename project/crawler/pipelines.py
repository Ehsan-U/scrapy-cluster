# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from sqlalchemy import insert, select
from scrapy import Spider
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional
from crawler.settings import POSTGRES_URI


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[Optional[str]]
    birth_year: Mapped[Optional[str]]
    street: Mapped[Optional[str]]
    city: Mapped[Optional[str]]
    region: Mapped[Optional[str]]
    zipcode: Mapped[Optional[str]]
    phone_1: Mapped[Optional[str]]
    phone_2: Mapped[Optional[str]]
    phone_3: Mapped[Optional[str]]
    phone_4: Mapped[Optional[str]]
    phone_5: Mapped[Optional[str]]


engine = create_async_engine(POSTGRES_URI)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class CrawlerPipeline:
    tables_created = False

    async def process_item(self, item, spider: Spider):
        if not self.tables_created:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self.tables_created = True

        async with async_session() as session:
            async with session.begin():
                select_stmt = select(Person).where(
                    Person.name == item.get("name") and Person.street == item.get("street",'') and Person.zipcode == item.get("zipcode", '')
                )
                row = await session.execute(select_stmt)
                try:
                    next(row)
                    spider.logger.info(f"Already exists: {item.get('name')}")
                except StopIteration:
                    insert_stmt = insert(Person).values(item)
                    await session.execute(insert_stmt)
                    await session.commit()
                    spider.logger.info(f"Added: {item.get('name')}")
        return item

