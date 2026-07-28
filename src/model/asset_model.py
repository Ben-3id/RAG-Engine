from .base_model import BaseModel
from sqlalchemy import Insert , Update , Delete , select , Select
from sqlalchemy.orm import joinedload
from .database.db_schema import Asset , Topic
from uuid import UUID


class AssetModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)

    async def add_asset(self , asset:Asset ):

        async with self.db_client as session:
            async with session.begin():
                session.add(asset)
            await session.commit()    
            await session.refresh(asset)
        return asset
    
    async def is_asset_accept(self , filehash:str):
        result = False
        async with self.db_client as session:
            async with session.begin():
                result = await session.execute(Select(Asset).where(Asset.filehash == filehash))
            result = bool(result.scalar_one_or_none())
        return result

    async def get_asset(self, topic_id:UUID , asset_id:UUID):
        result = None
        async with self.db_client as session:
            async with session.begin():
                result = await  session.execute(select(Asset)
                                                .options(joinedload(Asset.topic))
                                                .where(Asset.asset_id == asset_id ,Asset.topic_id == topic_id))
                result = result.scalar_one_or_none()
        return result

    async def get_all_topic_assets(self , topic_id:UUID):
        results = None
        async with self.db_client as session:
            async with session.begin():
                results = await session.execute(select(Asset).options(joinedload(Asset.topic)).where(Asset.topic_id == topic_id))
                results = results.scalars().all()
        return results

    async def delete_asset(self,asset:Asset):
        async with self.db_client as session:
            async with session.begin():
                await session.execute(Delete(Asset).where(Asset.asset_id == asset.asset_id))
            await session.commit()    
        return True

    async def delete_assets_by_topic(self,topic_id:UUID):
        async with self.db_client as session:
            async with session.begin():
                await session.execute(Delete(Asset).where(Asset.topic_id == topic_id))
            await session.commit()    
        return True