import os

from sqlmodel import create_engine, SQLModel, text, Session
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.getenv("DATABASE_ENGINE"), pool_size=int(os.getenv("DATABASE_POOL_SIZE", 10)))

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Генератор для получения сессий
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def check_availability(session: Session) -> bool:
    try:
        session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(e)
        return False