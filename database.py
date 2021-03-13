# from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, func
from config.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql.cursors


# engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    chat_id = Column(Integer, primary_key=True, autoincrement=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50))
    language_code = Column(String(10))
    tasks_limit = Column(Integer, default=10)  # Ограничение кол-ва принимаемых одновременно  в работу хэшей

    def __repr__(self):
        return f"<User(id={self.id}, fullname='{self.first_name} {self.last_name}', nickname={self.username})>"


class Wallet(Base):
    __tablename__ = 'wallet'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('users.chat_id'))
    btc = Column(Float, default=0)
    usd = Column(Float, default=0)
    rub = Column(Float, default=0)


class Task(Base):
    __tablename__ = 'tasks'

    taskwrapper_id = Column(Integer, primary_key=True, autoincrement=False)
    chat_id = Column(Integer, ForeignKey('users.chat_id'))
    hashlist_id = Column(Integer)      # аналогичен значению поля hashtopolis.Hashlist(hashlistId)
    supertask_id = Column(Integer)     # аналогичен значению поля hashtopolis.Supertask(supertaskId)
    completed = Column(Boolean)         # Признак того, что выполнение задачи завершено
    priority = Column(Integer)


class Hashe(Base):
    __tablename__ = 'hashes'
    id = Column(Integer, primary_key=True)
    hash_id = Column(Integer, unique=False)  # аналогичен значению поля hashtopolis.Hash(hashId)
    taskwrapper_id = Column(Integer, ForeignKey('tasks.taskwrapper_id'))
    is_cracked = Column(Boolean, default=False)     # признак того, что пароль найден
    is_send = Column(Boolean, default=False)        # Признак того, что пароль отправлен пользователю в чат


class Supertask(Base):
    __tablename__ = 'supertask'

    id = Column(Integer, primary_key=True, autoincrement=False)  # аналогичен значению поля hashtopolis.Supertask(supertaskId)
    name = Column(String(100), nullable=False)  # аналогичен значению поля hashtopolis.Supertask(supertaskName)
    price = Column(Float)  # стоимость за хэш


class DatabaseTlgBot:
    __instance = None

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.session = None
        self.engine = None
        self.connect()

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DatabaseTlgBot, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def _create_tables(self, table):
        Base.metadata.create_all(self.engine, tables=table)

    def connect(self, host=settings.DB_HOST, user=settings.DB_USER,
                 password=settings.DB_PASSWORD, db_name=settings.DB_NAME):
        if not self.session:
            self.engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            return self.session

    def close(self):
        self.session.close()
        self.close_engine()

    def close_engine(self):
        self.engine.dispose()

    def check_user_exist(self, chat_id):
        return self.session.query(User.chat_id).filter(User.chat_id == chat_id).scalar()

    def create_user(self, chat_id, first_name, last_name, username, language_code, tasks_limit=10):
        if self.check_user_exist(chat_id=chat_id):
            return
        user = User(chat_id=chat_id, first_name=first_name, last_name=last_name, username=username,
                    language_code=language_code, tasks_limit=tasks_limit)
        wallet = Wallet(chat_id=chat_id)
        self.session.add(user)
        self.session.commit()
        self.session.add(wallet)
        self.session.commit()

    def get_count_active_task_for_user(self, chat_id):
        return self.session.query(Task).filter(Task.chat_id == chat_id).filter(Task.completed is False).count()

    def get_supertasks_info(self):
        return self.session.query(Supertask).all()

    def get_last_priority(self) -> int:
        return self.session.query(func.min(Task.priority)).filter(Task.completed == 0).one()[0]

    def get_taskwrapper_max_id(self):
        max_id = self.session.query(func.max(Task.taskwrapper_id)).one()[0]
        if max_id > 1000000:
            return max_id + 1
        if not max_id:
            return 1000000
        return max_id + 1000000

    def allowed_accept_tasks(self, chat_id):
        task_limit_user = self.session.query(User.tasks_limit).filter(User.chat_id == chat_id).scalar()
        if task_limit_user:
            if self.get_count_active_task_for_user(chat_id) < task_limit_user:
                return True
        return False

    def add_task(self, taskwrapper_id, chat_id, hashlist_id, supertask_id, priority):
        task = Task(taskwrapper_id=taskwrapper_id, chat_id=chat_id, hashlist_id=hashlist_id,
                    supertask_id=supertask_id, priority=priority)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

    def add_hash(self, taskwrapper_id: int, hashes_id: list, is_cracked: int = 0):
        for hash_id in hashes_id:
            hash = Hashe(taskwrapper_id=taskwrapper_id, hash_id=hash_id, is_cracked=is_cracked)
            self.session.add(hash)
        self.session.commit()


class DatabaseHashtopolis:
    def __init__(self):
        self.connection = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER, password=settings.DB_PASSWORD,
                                          database=settings.DB_NAME_HASHTOPOLIS, cursorclass=pymysql.cursors.DictCursor)

    def get_hash_id(self, hashlist_id: int = None, hash: str = None) -> list:
        """
        Возвращает hashId из Hashtopolis.Hash. В зависимости от полученного аргумента возвращает hashId всех хэшей,
        принадлежащих одному hashlist (аргумент hashlist_id) или
        hashId одного хэша, полученного в виде строки (аргумент hash).
        :param hashlist_id: id hashlist
        :param hash: hash
        :return: Список hashId
        """
        with self.connection.cursor() as cursor:
            if hashlist_id:
                sql = "SELECT `hashId` FROM `Hash` WHERE `hashlistId`=%s"
                cursor.execute(sql, (hashlist_id,))
            if hash:
                sql = f"SELECT `hashId` FROM `Hash` WHERE `hash`='{hash}' LIMIT 1"
                print(sql)
                cursor.execute(sql)
            result = cursor.fetchall()
            return [i.get('hashId') for i in result]

    def check_cracked_hash_for_taskwrapper(self, taskwrapper_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT h.hashId, h.plaintext FROM Hash h JOIN TaskWrapper tw ON tw.hashlistId = h.hashlistId " \
                  "WHERE tw.taskWrapperId = %s AND h.isCracked = 1;"
            cursor.execute(sql, (taskwrapper_id,))
            return cursor.fetchall()

    def check_hashes_in_available(self, hashlist: list) -> list:
        """
        Функция проверяет хэши по базе и возвращает хэш и пароль
        :param hashlist:
        :return:
        """
        with self.connection.cursor() as cursor:
            sql = 'SELECT DISTINCT (hash), plaintext FROM Hash WHERE Hash IN ("{}") AND isCracked = 1;' \
                .format('","'.join(hashlist))
            print(sql)
            cursor.execute(sql)
            return cursor.fetchall()


if __name__ == '__main__':
    # db = DatabaseTlgBot()
    # print(db.get_taskwrapper_max_id())
    db = DatabaseHashtopolis()
    # hashlist = ['004823ba55c79cd95a331b1283d8cbfc',
    #             '0096f31cafba65a4719b644fdda7d885',
    #             '00f3907872e28ec3cbd7608f3efc728f',
    #             '0126e02d0a062ae96bb9f6053d26ef17',
    #             '01a88086180795d2cc9a2d9ea348521d', ]
    res = db.get_hash_id(hash='004823ba55c79cd95a331b1283d8cbfc')
    # print(type(res))
    # for i in range(10):
    # create_user(chat_id=123123, first_name='123', last_name='312', username='111', language_code='ке')
    # db.connect()
    # table_object = [Supertask.__table__, User.__table__, Wallet.__table__, Task.__table__, Hashe.__table__]
    # db.drop_tables(table_object)
    # db._create_tables(table_object)
    # res = db.get_last_priority()
    # print(res)
    # if not db.check_user_exist(123):
    #     print('not user')
    # db.close()
    # db.close_engine()
    # db = DatabaseHashtopolis()
    # print(db.get_hash_id(6340))
