from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import validator


class ProdutoBase(SQLModel):
	nome: str = Field(..., min_length=3, max_length=60)
	descricao: Optional[str] = None
	preco: float = Field(..., ge=0.01)
	estoque: int = Field(..., ge=0)
	categoria: str = Field(..., min_length=1)
	sku: Optional[str] = None

	@validator('preco')
	def preco_duas_casas(cls, v):
		# garantir duas casas (representação simples)
		return round(float(v), 2)


class Produto(ProdutoBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)


class ProdutoRead(ProdutoBase):
	id: int

