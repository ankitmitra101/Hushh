import { useTheme } from '../context/ThemeContext'
import './LandingPage.css'

const LandingPage = ({ onGetStarted }) => {
 const { isDark, toggleTheme } = useTheme()

 const categories = [
  { id: 'sneakers', icon: '👟', name: 'Sneakers', desc: 'Running, casual & lifestyle' },
  { id: 'tshirts', icon: '👕', name: 'T-Shirts', desc: 'Casual, minimal & street' },
  { id: 'accessories', icon: '🎒', name: 'Accessories', desc: 'Belts, bags & eyewear' },
 ]

 const features = [
  { icon: '🧠', title: 'Smart Memory', desc: 'Remembers what you like and avoids what you don\'t' },
  { icon: '🎯', title: 'Personalized', desc: 'AI-curated results matching your style' },
  { icon: '💬', title: 'Natural Chat', desc: 'Just describe what you want in plain words' },
 ]

 return (
  <div className="landing">
   {/* Theme Toggle */}
   <button className="theme-btn" onClick={toggleTheme} aria-label="Toggle theme">
    {isDark ? (
     <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="5" />
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
     </svg>
    ) : (
     <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
     </svg>
    )}
   </button>

   {/* Hero Section */}
   <section className="hero">
    <div className="hero-content">
     <div className="brand">
      <div className="brand-logo">
       <span>H</span>
      </div>
      <h1 className="brand-name">Hushh</h1>
     </div>

     <p className="tagline">Your Personal AI Shopping Concierge</p>

     <p className="hero-desc">
      Tell me what you're looking for in your own words.
      I'll remember your preferences and find the perfect match.
     </p>
    </div>
   </section>

   {/* Categories */}
   <section className="categories">
    <h2>What are you shopping for?</h2>
    <div className="category-grid">
     {categories.map((cat) => (
      <button
       key={cat.id}
       className="category-card"
       onClick={() => onGetStarted(cat.id)}
      >
       <span className="category-icon">{cat.icon}</span>
       <div className="category-info">
        <strong>{cat.name}</strong>
        <span>{cat.desc}</span>
       </div>
       <svg className="category-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M5 12h14M12 5l7 7-7 7" />
       </svg>
      </button>
     ))}
    </div>
   </section>

   {/* Features */}
   <section className="features">
    <div className="features-grid">
     {features.map((feature, idx) => (
      <div key={idx} className="feature-card">
       <span className="feature-icon">{feature.icon}</span>
       <strong>{feature.title}</strong>
       <p>{feature.desc}</p>
      </div>
     ))}
    </div>
   </section>

   {/* CTA */}
   <section className="cta">
    <button className="cta-btn" onClick={() => onGetStarted('explore')}>
     Start Shopping
     <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M5 12h14M12 5l7 7-7 7" />
     </svg>
    </button>
    <p className="cta-hint">No signup required</p>
   </section>

   {/* Footer */}
   <footer className="landing-footer">
    <p>Powered by Groq AI</p>
   </footer>
  </div>
 )
}

export default LandingPage
