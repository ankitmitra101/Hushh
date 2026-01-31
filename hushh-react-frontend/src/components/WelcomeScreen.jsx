import './WelcomeScreen.css'

const WelcomeScreen = ({ onSuggestionClick, initialCategory }) => {
 const getSuggestions = () => {
  switch (initialCategory) {
   case 'sneakers':
    return [
     { text: 'White sneakers' },
     { text: 'Minimal running shoes' },
     { text: 'Black casual sneakers' },
    ]
   case 'tshirts':
    return [
     { text: 'Casual cotton t-shirts' },
     { text: 'Minimal white tees' },
     { text: 'Black oversized shirts' },
    ]
   case 'accessories':
    return [
     { text: 'Classic leather belt' },
     { text: 'Minimal sunglasses' },
     { text: 'Everyday backpack' },
    ]
   default:
    return [
     { text: 'White sneakers' },
     { text: 'Casual t-shirts' },
     { text: 'Minimal style items' },
    ]
  }
 }

 const suggestions = getSuggestions()

 return (
  <div className="welcome-screen">
   <div className="welcome-content">
    <div className="welcome-icon">
     <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z" />
     </svg>
    </div>

    <h2>What are you looking for?</h2>
    <p className="welcome-subtitle">
     Describe in your own words. I'll learn your preferences.
    </p>

    <div className="quick-suggestions">
     {suggestions.map((item, idx) => (
      <button
       key={idx}
       className="suggestion-pill"
       onClick={() => onSuggestionClick(item.text)}
      >
       {item.text}
      </button>
     ))}
    </div>

    <div className="tips">
     <p>
      <strong>Tip:</strong> Say things like "avoid chunky" or "no oversized" to filter styles
     </p>
    </div>
   </div>
  </div>
 )
}

export default WelcomeScreen
