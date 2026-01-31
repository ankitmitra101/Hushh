import { useTheme } from '../context/ThemeContext'
import './Header.css'

const Header = ({ backendStatus, onTestConnection, onBack, showBack }) => {
 const { isDark, toggleTheme } = useTheme()

 return (
  <header className="header">
   <div className="header-content">
    <div className="header-left">
     {showBack && (
      <button className="back-btn" onClick={onBack} aria-label="Back to home">
       <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M19 12H5M12 19l-7-7 7-7" />
       </svg>
      </button>
     )}

     <div className="logo">
      <div className="logo-icon">
       <span className="logo-letter">H</span>
      </div>
      <div className="logo-text">
       <h1>Hushh</h1>
       <span className="logo-subtitle">AI Shopping Concierge</span>
      </div>
     </div>
    </div>

    <div className="header-actions">
     {/* Theme Toggle */}
     <button
      className="theme-toggle"
      onClick={toggleTheme}
      aria-label="Toggle theme"
     >
      {isDark ? (
       <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="5" />
        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
       </svg>
      ) : (
       <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
       </svg>
      )}
     </button>

     {/* Status Badge */}
     <div className={`status-badge ${backendStatus}`} onClick={onTestConnection}>
      <span className="status-dot"></span>
      <span className="status-text">
       {backendStatus === 'online' ? 'AI Ready' : backendStatus === 'checking' ? 'Connecting...' : 'Offline'}
      </span>
     </div>
    </div>
   </div>
  </header>
 )
}

export default Header
