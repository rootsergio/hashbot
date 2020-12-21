from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey

engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    language_code = Column(String)
    is_bot = Column(Boolean)
    balance = Column(Float)

    def __repr__(self):
        return f"<User(id={self.id}, fullname='%s', nickname={self.username})>"


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    completed = Column(Boolean) # Признак того, что выполнение задачи завершено
    hash_list_id = Column(Integer)
    hash_type_id = Column(String)
    taskWrapper_id = Column(Integer)
    super_task_id = Column(Integer)


class Hashes(Base):
    __tablename__ = 'hashes'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    hash = Column(String)
    salt = Column(String)
    plaintext = Column(String)
    is_send = Column(Boolean)   # Признак того, что пароль отправлен пользователю