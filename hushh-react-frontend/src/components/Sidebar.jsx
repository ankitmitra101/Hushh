import './Sidebar.css'

const Sidebar = ({
 userName,
 userId,
 avoidKeywords,
 sessionData,
 onRemoveKeyword,
 onClearChat
}) => {
 return (
  <aside className="sidebar">
   {/* User Profile Card */}
   <div className="sidebar-card profile-card">
    <div className="profile-avatar">
     <span>{userName.charAt(0)}</span>
     <div className="avatar-ring"></div>
    </div>
    <div className="profile-info">
     <span className="profile-name">{userName}</span>
     <span className="profile-id">@{userId}</span>
    </div>
    <div className="profile-badge">Pro</div>
   </div>

   {/* Avoided Items */}
   <div className="sidebar-card">
    <div className="card-header">
     <h3>Avoided Styles</h3>
     {avoidKeywords.length > 0 && (
      <span className="count-badge">{avoidKeywords.length}</span>
     )}
    </div>

    {avoidKeywords.length > 0 ? (
     <div className="avoid-list">
      {avoidKeywords.map((keyword, idx) => (
       <div key={idx} className="avoid-chip">
        <span>{keyword}</span>
        <button
         onClick={() => onRemoveKeyword(keyword)}
         className="chip-remove"
         aria-label={`Remove ${keyword}`}
        >
         <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 6L6 18M6 6l12 12" />
         </svg>
        </button>
       </div>
      ))}
     </div>
    ) : (
     <div className="empty-state">
      <div className="empty-icon">
       <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" />
       </svg>
      </div>
      <p>No filters yet</p>
      <span>Try "avoid chunky" or "no oversized"</span>
     </div>
    )}
   </div>

   {/* Session Context */}
   <div className="sidebar-card">
    <div className="card-header">
     <h3>Current Search</h3>
    </div>

    <div className="session-grid">
     <div className={`session-item ${sessionData.category ? 'filled' : ''}`}>
      <span className="session-label">Category</span>
      <span className="session-value">{sessionData.category || '—'}</span>
     </div>
     <div className={`session-item ${sessionData.budget ? 'filled' : ''}`}>
      <span className="session-label">Budget</span>
      <span className="session-value">
       {sessionData.budget ? `₹${sessionData.budget}` : '—'}
      </span>
     </div>
     <div className={`session-item ${sessionData.size ? 'filled' : ''}`}>
      <span className="session-label">Size</span>
      <span className="session-value">{sessionData.size || '—'}</span>
     </div>
    </div>
   </div>

   {/* Quick Actions */}
   <div className="sidebar-actions">
    <button className="action-btn secondary" onClick={onClearChat}>
     <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
     </svg>
     New Search
    </button>
   </div>
  </aside>
 )
}

export default Sidebar
