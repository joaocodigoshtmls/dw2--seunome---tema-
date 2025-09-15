from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional, List, Tuple
from sqlmodel import select

from .database import engine, init_db, get_session
from .models import Produto, ProdutoRead
from .models import ProdutoCreate, ProdutoUpdate
from fastapi import status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # retornar 422 com erros por campo em português
    return JSONResponse(status_code=422, content={"erro": str(exc)} )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    # log exc se necessário (aqui apenas retorno genérico)
    return JSONResponse(status_code=500, content={"erro":"erro interno no servidor"})


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



@app.post('/produtos', response_model=ProdutoRead, status_code=status.HTTP_201_CREATED)
def create_produto(prod_in: ProdutoCreate):
    session = get_session()
    produto = Produto.from_orm(prod_in)
    try:
        session.add(produto)
        session.commit()
        session.refresh(produto)
    except IntegrityError as e:
        session.rollback()
        # assumir que é violação de unique sku
        raise HTTPException(status_code=400, detail={'erro':'sku deve ser único'})
    return produto


@app.put('/produtos/{produto_id}', response_model=ProdutoRead)
def update_produto(produto_id: int, prod_in: ProdutoUpdate):
    session = get_session()
    produto = session.get(Produto, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail={'erro':'produto não encontrado'})
    prod_data = prod_in.dict(exclude_unset=True)
    for key, value in prod_data.items():
        setattr(produto, key, value)
    try:
        session.add(produto)
        session.commit()
        session.refresh(produto)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail={'erro':'sku deve ser único'})
    return produto


@app.delete('/produtos/{produto_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_produto(produto_id: int):
    session = get_session()
    produto = session.get(Produto, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail={'erro':'produto não encontrado'})
    session.delete(produto)
    session.commit()
    return None
