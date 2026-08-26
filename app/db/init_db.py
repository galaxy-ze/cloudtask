from app.db.base import Base
from app.db.database import engine
from app.models.user import User

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database table created.")