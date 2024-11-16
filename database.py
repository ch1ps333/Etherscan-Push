from sqlalchemy import create_engine, Column, Integer, BigInteger, ForeignKey, String, Text, Boolean, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from os import getenv
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"mysql+aiomysql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_SCHEME')}"
async_engine = create_async_engine(DATABASE_URL, pool_recycle=299, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)


DATABASE_URL = f"mysql+pymysql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_SCHEME')}"
engine = create_engine(DATABASE_URL, pool_recycle=299, pool_pre_ping=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Groups(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(300))
    transactionSum = Column(Integer)
    min_amount = Column(Integer)
    max_amount = Column(Integer)
    status = Column(Boolean)


class Addresses(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    group_id = Column(BigInteger, ForeignKey('groups.tg_id'), nullable=False) 
    address = Column(String(300))
    transactions_from = Column(Boolean)
    transactions_to = Column(Boolean)

    group = relationship('Groups', backref='addresses')

class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    info_collect_interval_from = Column(Integer)
    info_collect_interval_to = Column(Integer)
    template_message = Column(Text)
    photo_id = Column(String(300))
    gif_id = Column(String(300))
    file_type = Column(String(10))

class Admins(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)


async def reg_group(tg_id, group_name):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Groups).filter_by(tg_id=tg_id))
            existing_group = result.scalar()
            if existing_group:
                return False
            else:
                user = Groups(
                    tg_id=tg_id,
                    name=group_name,
                    min_amount=1,
                    max_amount=1000000,
                    transactionSum=0,
                    status=True
                )
                session.add(user)
                await session.commit()
                return True
        except SQLAlchemyError as err:
            print(err)
            return False
        
async def set_group_amount_for_search(state, group_id, amount):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Groups).filter_by(tg_id=group_id))
            group = result.scalar()
            if state == 'min':
                group.min_amount = amount
            elif state == 'max':
                group.max_amount = amount
            await session.commit()
            return True
        except SQLAlchemyError as err:
            print(err)
            return False
        
async def add_group_transaction_sum(group_id, amount):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Groups).filter_by(tg_id=group_id))
            group = result.scalar()
            group.transactionSum += amount
            await session.commit()
            return True
        except SQLAlchemyError as err:
            print(err)
            return False
        
async def set_group_status(group_id, status):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Groups).filter_by(tg_id=group_id))
            group = result.scalar()
            group.status = status
            await session.commit()
            return True
        except SQLAlchemyError as err:
            print(err)
            return False

async def add_address(address, group_id):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Addresses))
            address = Addresses(
                group_id=group_id,
                address=address,
                transactions_from=True,
                transactions_to=True
            )
            session.add(address)
            await session.commit()
            return True
            
        except SQLAlchemyError as err:
            print(err)
            return False
        
async def get_address(address, group_id):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Addresses).filter(Addresses.group_id == group_id, Addresses.address == address)
            )
            address = result.scalars().one_or_none()
            return address
        except SQLAlchemyError as err:
            print(err)
            return None
        
async def set_address_to_from(address, group_id, type, state):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Addresses).filter(Addresses.group_id == group_id, Addresses.address == address)
            )
            address = result.scalars().one_or_none()
            if type == 'to':
                address.transactions_to = state
            elif type == 'from':
                address.transactions_from = state
            await session.commit()
            return True
        except SQLAlchemyError as err:
            print(err)
            return False

async def create_config():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Config))
            config = result.scalars().first() 
            if config is None:
                config = Config(
                    info_collect_interval_from=5,
                    info_collect_interval_to=10,
                    gif_id="CgACAgQAAxkBAAIx_WcyUkhEz2GwhlnRUuAGZaQmT0ZxAAL3AgACHC8NU7aJhu3A3mmENgQ",
                    file_type='gif'
                )
                session.add(config)
                await session.commit()
                
        except SQLAlchemyError as err:
            print(err)

async def add_admin(tg_id):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Admins).filter_by(tg_id=tg_id))
            admin_exist = result.scalars().first() 
            if admin_exist:
                return False
            admin = Admins(
                tg_id=tg_id
            )
            session.add(admin)
            await session.commit()
            return True
        except SQLAlchemyError as err:
            print(err)

async def get_admins():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Admins))
            admins = result.scalars().all() 
            return admins
        except SQLAlchemyError as err:
            print(err) 
            return None  

async def remove_admin(tg_id: int):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Admins).filter(Admins.tg_id == tg_id))
            admin = result.scalar_one_or_none()

            if admin:
                await session.delete(admin)
                await session.commit()
                return True
            else:
                return False
    
        except SQLAlchemyError as err:
            print(f"Ошибка при удалении администратора: {err}")
            await session.rollback()
            return False
            

async def get_config():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Config))
            config = result.scalars().first() 
            return config
                
        except SQLAlchemyError as err:
            print(err)

async def get_group_trans_sum(group_id: int):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Groups).filter_by(tg_id=group_id))
            group = result.scalars().first() 
            return group.transactionSum
                
        except SQLAlchemyError as err:
            print(err)

async def get_group(group_id):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Groups).filter_by(tg_id=group_id))
            group = result.scalars().first() 
            return group
                
        except SQLAlchemyError as err:
            print(err)


async def change_template(text):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Config))
            config = result.scalars().first() 
            config.template_message = text
            await session.commit()
            return True
        except SQLAlchemyError as err:
            print(err)
            return False
        
async def change_file(type, file_id):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Config))
            config = result.scalars().first() 
            if type == 'photo':
                config.photo_id = file_id
                config.file_type = 'photo'
            elif type == 'gif':
                config.gif_id = file_id
                config.file_type = 'gif'
                
            await session.commit()
            return True
        except SQLAlchemyError as err:
            print(err)
            return False
        
async def change_interval(interval_from, interval_to):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Config))
            config = result.scalars().first() 
            config.info_collect_interval_from = interval_from
            config.info_collect_interval_to = interval_to
            await session.commit()
            return True
        except SQLAlchemyError as err:
            print(err)
            return False
        


async def get_all_groups():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Groups))
            groups = result.scalars().all()
            return groups
        except SQLAlchemyError as err:
            print(err)
            return []
        
async def get_addresses(group_id: int):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Addresses).filter_by(group_id=group_id))
            addresses = result.scalars().all()
            address_strings = [address.address for address in addresses]

            return address_strings
        except SQLAlchemyError as err:
            print(err)
            return []

    

async def delete_group(tg_id: int):
    async with AsyncSessionLocal() as session:
        try:
            delete_addresses_stmt = delete(Addresses).where(Addresses.group_id == tg_id)
            await session.execute(delete_addresses_stmt)
            
            result = await session.execute(select(Groups).filter(Groups.tg_id == tg_id))
            group = result.scalar_one_or_none()

            if group:
                await session.delete(group)
                await session.commit()
                return True
            else:
                return False

        except SQLAlchemyError as err:
            print(f"Ошибка при удалении группы: {err}")
            await session.rollback()
            return False
        
async def delete_address(group_id: int, address: str):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Addresses).filter(Addresses.group_id == group_id, Addresses.address == address)
            )
            addresses_to_delete = result.scalars().all()

            if addresses_to_delete:
                for address_to_delete in addresses_to_delete:
                    await session.delete(address_to_delete)
                await session.commit()
                return True
            else:
                return False
    
        except SQLAlchemyError as err:
            print(f"Ошибка при удалении адреса: {err}")
            await session.rollback()
            return False
        
async def rename_address(address, group_id: int, new_name):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Addresses).filter(Addresses.group_id == group_id, Addresses.address == address)
            )
            addresses_to_rename = result.scalars().all()
            if addresses_to_rename:
                for address_to_rename in addresses_to_rename:
                    address_to_rename.address = new_name
                await session.commit()
                return True
            return False
        except SQLAlchemyError as err:
            print(err)
            return False
