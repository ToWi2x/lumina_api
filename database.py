from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. The Database URL (Creates a file named lumina.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./lumina.db"

# 2. The Engine (Drives SQL commands to the database)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. The Session (Used to talk to the DB for each web request)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. The Base (Equivalent to Django's models.Model)
Base = declarative_base()