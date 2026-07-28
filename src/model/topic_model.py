from sqlalchemy import Insert , Select , Delete , Update
from .base_model import BaseModel
from .database.db_schema import Topic 
from typing import Union


class TopicModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)


    async def create_topic(self,topic: str | Topic ):
        if isinstance(topic, str):
            topic = Topic(topic_name = topic)

        async with self.db_client as session:
            async with session.begin():
               session.add(topic)
            await session.commit()    
            await session.refresh(topic)

        return topic


    async def get_topic_or_create(self,topic:Union[str , Topic]):
        if isinstance(topic, str):
            topic = Topic(topic_name=topic)

        if await self.is_topic_exists(topic.topic_name):

            async with self.db_client as session:
                async with session.begin():
                    result = await session.execute(Select(Topic).where(Topic.topic_name == topic.topic_name))
                    topic = result.scalar_one()
        else:
            topic = await self.create_topic(topic)
        return topic


    async def delete_topic(self,topic: str | Topic):
        if isinstance(topic, Topic):
            topic = topic.topic_name
                    
        async with self.db_client as session:
            async with session.begin():
                await session.execute(Delete(Topic).where(Topic.topic_name == topic))
            await session.commit()
        return True

    async def edit_description(self , topic: str | Topic , description: str):
        if isinstance(topic, Topic):
            topic = topic.topic_name

        async with self.db_client as session:
            async with session.begin():
                await session.execute(Update(Topic).where(Topic.topic_name == topic).values(topic_description = description))
            await session.commit()
        return True
    
    async def get_topics(self):
        results = None
        async with self.db_client as session:
            async with session.begin():
                results = await session.execute(Select(Topic))
                results = results.scalars().all()
        return [{"topic_id": object.topic_id ,
                  "topic_name":object.topic_name ,
                    "topic_description":object.topic_description }
                for object in results]

    async def is_topic_exists(self, topic_name: str | Topic ):

        results = None
        async with self.db_client as session:
            async with session.begin():
                results = await session.execute(Select(Topic).where(Topic.topic_name == topic_name))
                results = bool(results.scalar_one_or_none())
        return results