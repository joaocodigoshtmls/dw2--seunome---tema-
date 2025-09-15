from sqlmodel import SQLModel, create_engine
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./vendas.db')

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db():
    SQLModel.metadata.create_all(engine)
    # garantir índice UNIQUE em sku (método simples sem migração completa)
    with engine.connect() as conn:
        conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_produto_sku ON produto (sku);
        """)


def get_session():
    from sqlmodel import Session
    return Session(engine)
