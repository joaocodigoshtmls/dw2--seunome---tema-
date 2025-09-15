from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional, List, Tuple
from sqlmodel import select

from .database import engine, init_db, get_session
from .models import Produto, ProdutoRead


app = FastAPI(title='VENDAS - Backend')


@app.on_event('startup')
def on_startup():
    init_db()


@app.get('/health')
def health():
    return {"status": "ok"}


@app.get('/produtos', response_model=List[ProdutoRead])
def list_produtos(
    search: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    sort: Optional[str] = Query(None, description='nome|preco:(asc|desc)'),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    session = get_session()
    query = select(Produto)
    if search:
        query = query.where(Produto.nome.ilike(f"%{search}%"))
    if categoria:
        query = query.where(Produto.categoria == categoria)

    # ordenacao
    if sort:
        try:
            field, direction = sort.split(':')
            direction = direction.lower()
            if field == 'nome':
                if direction == 'asc':
                    query = query.order_by(Produto.nome)
                else:
                    query = query.order_by(Produto.nome.desc())
            elif field == 'preco':
                if direction == 'asc':
                    query = query.order_by(Produto.preco)
                else:
                    query = query.order_by(Produto.preco.desc())
        except Exception:
            raise HTTPException(status_code=400, detail='sort inválido')

    # paginação simples
    offset = (page - 1) * limit
    results = session.exec(query.offset(offset).limit(limit)).all()
    return results
