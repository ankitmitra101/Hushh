import './ProductGrid.css'

const ProductGrid = ({ products }) => {
 const getCategoryIcon = (category) => {
  switch (category) {
   case 'footwear': return '👟'
   case 'apparel': return '👕'
   case 'accessories': return '🎒'
   default: return '🛍️'
  }
 }

 return (
  <div className="product-grid">
   <div className="grid-header">
    <span className="grid-title">Found {products.length} matches</span>
   </div>

   <div className="grid-items">
    {products.map((product, idx) => (
     <article key={idx} className="product-card" style={{ animationDelay: `${idx * 0.1}s` }}>
      <div className="product-image">
       <span className="product-icon">{getCategoryIcon(product.category)}</span>

       {product.match_score && (
        <div className="match-badge">
         <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
          <path d="M20 6L9 17l-5-5" />
         </svg>
         <span>{Math.round(product.match_score * 100)}%</span>
        </div>
       )}
      </div>

      <div className="product-info">
       <span className="product-brand">{product.brand}</span>
       <h4 className="product-title">{product.title}</h4>

       <div className="product-meta">
        <span className="product-price">₹{product.price_inr?.toLocaleString()}</span>
        {product.size && (
         <span className="product-size">Size {product.size}</span>
        )}
       </div>
      </div>

      <button className="product-action">
       View Details
       <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M5 12h14M12 5l7 7-7 7" />
       </svg>
      </button>
     </article>
    ))}
   </div>
  </div>
 )
}

export default ProductGrid
