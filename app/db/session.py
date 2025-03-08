from app.db.base import SessionLocal

def get_db():
    """
    Dependency for database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()