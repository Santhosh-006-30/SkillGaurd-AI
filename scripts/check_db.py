import os
import sys

# Ensure backend path is on sys.path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database.database import engine, Base
import app.database.models  # load all models so metadata knows them

def init_and_check():
    Base.metadata.create_all(bind=engine)
    print("Database metadata initialized.")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"  - Model Table: {table_name}")

if __name__ == "__main__":
    init_and_check()
