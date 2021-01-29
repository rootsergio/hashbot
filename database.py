# from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from config.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50))
    language_code = Column(String(10))
    is_bot = Column(Boolean)
    hashes_limit = Column(Integer, default=10)  # Ограничение кол-ва принимаемых одновременно  в работу хэшей
    wallet_id = Column(Integer, ForeignKey('wallet.id'))

    def __repr__(self):
        return f"<User(id={self.id}, fullname='{self.first_name} {self.last_name}', nickname={self.username})>"


class Wallet(Base):
    __tablename__ = 'wallet'

    id = Column(Integer, primary_key=True)
    btc = Column(Float, default=0)
    usd = Column(Float, default=0)
    rub = Column(Float, default=0)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hash_list_id = Column(Integer)
    task_wrapper_id = Column(Integer)
    completed = Column(Boolean)  # Признак того, что выполнение задачи завершено


class Hashe(Base):
    __tablename__ = 'hashes'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    hash_id = Column(Integer)
    is_cracked = Column(Boolean)
    is_send = Column(Boolean)   # Признак того, что пароль отправлен


class Database:
    def __init__(self, host=settings.DB_HOST, user=settings.DB_USER,
                 password=settings.DB_PASSWORD, db_name=settings.DB_NAME):
        self.session = None
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

    def connect(self):
        engine = create_engine(f'mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.db_name}')
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)  # Создание таблиц
        return self.session


if __name__ == '__main__':
    db = Database()
    session = db.connect()
    session.close()
