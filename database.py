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
    tasks_limit = Column(Integer, default=10)  # Ограничение кол-ва принимаемых одновременно  в работу хэшей
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
    chat_id = Column(Integer, ForeignKey('users.chat_id'))
    hash_list_id = Column(Integer)
    task_wrapper_id = Column(Integer)
    supertask_id = Column(Integer, ForeignKey('supertask.id'))
    completed = Column(Boolean)  # Признак того, что выполнение задачи завершено


class Hashe(Base):
    __tablename__ = 'hashes'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    hash_id = Column(Integer)
    is_cracked = Column(Boolean)
    is_send = Column(Boolean)   # Признак того, что пароль отправлен


class Supertask(Base):
    __tablename__ = 'supertask'

    id = Column(Integer, primary_key=True, autoincrement=False)
    price = Column(Float)


class Database:
    def __init__(self, ):
        self.session = None
        self.engine = None
        self.connect()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def close(self):
        self.session.close()

    def close_engine(self):
        self.engine.dispose()

    def connect(self, host=settings.DB_HOST, user=settings.DB_USER,
                 password=settings.DB_PASSWORD, db_name=settings.DB_NAME):
        self.engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_tables(self, table):
        Base.metadata.create_all(self.engine, tables=table)

    def check_user(self, chat_id):
        return self.session.query(User.id).filter(User.chat_id == chat_id).scalar()

    def create_user(self, chat_id, first_name, last_name, username, language_code, hashes_limit=10, wallet_id=None):
        user = User(chat_id=chat_id, first_name=first_name, last_name=last_name, username=username,
                    language_code=language_code, hashes_limit=hashes_limit, wallet_id=wallet_id)
        self.session.add(user)
        self.session.commit()

    def get_count_active_task_for_user(self, chat_id):
        return self.session.query(Task).filter(Task.chat_id == chat_id).filter(Task.completed is False).count()

    def allowed_accept_tasks(self, chat_id):
        task_limit_user = self.session.query(User.tasks_limit).filter(User.chat_id == chat_id).scalar()
        if task_limit_user:
            if self.get_count_active_task_for_user(chat_id) < task_limit_user:
                return True
        return False

    def get_supertasks(self):
        return self.session.query(Supertask.id).all()
        # return [i[0] for i in result]

    def add_task(self, chat_id, hash_list_id, supertask_id, task_wrapper_id):
        task = Task(chat_id=chat_id, hash_list_id=hash_list_id, task_wrapper_id=task_wrapper_id, supertask_id=supertask_id)
        self.session.add(task)
        self.session.commit()


if __name__ == '__main__':
    db = Database()
    db.connect()
    table_object = [Task.__table__]
    db.create_tables(table_object)
    # print(db.get_active_task_for_user(123123))
    # db.get_supertasks()
    db.close()
    db.close_engine()

