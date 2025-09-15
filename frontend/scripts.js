document.getElementById('open-cart').addEventListener('click', ()=>{
  document.getElementById('cart-drawer').classList.remove('hidden')
})
document.getElementById('close-cart').addEventListener('click', ()=>{
  document.getElementById('cart-drawer').classList.add('hidden')
})

// placeholder para futuros carregamentos de produtos
document.addEventListener('DOMContentLoaded', ()=>{
  fetchProdutos()
})


function fetchProdutos(){
  const container = document.getElementById('produtos')
  container.innerHTML = ''
  fetch('/produtos')
    .then(r => r.json())
    .then(data => {
      if(!Array.isArray(data) || data.length===0){
        container.innerHTML = '<div class="placeholder">Nenhum produto disponível</div>'
        return
      }
      data.forEach(prod => {
        const card = document.createElement('div')
        card.className = 'card'
        card.innerHTML = `
          <img src="https://via.placeholder.com/400x200?text=Imagem" alt="${prod.nome}" />
          <div class="nome">${prod.nome}</div>
          <div class="preco">R$ ${Number(prod.preco).toFixed(2)}</div>
          <div class="estoque">Em estoque: ${prod.estoque}</div>
        `
        container.appendChild(card)
      })
    })
    .catch(err=>{
      container.innerHTML = '<div class="placeholder">Erro ao carregar produtos</div>'
      console.error('fetchProdutos erro', err)
    })
}
