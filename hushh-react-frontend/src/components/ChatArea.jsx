import './ChatArea.css'
import WelcomeScreen from './WelcomeScreen'
import Message from './Message'
import ProductGrid from './ProductGrid'

const ChatArea = ({
 messages,
 isLoading,
 input,
 onInputChange,
 onSend,
 onSuggestionClick,
 messagesEndRef,
 initialCategory
}) => {
 const handleKeyPress = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
   e.preventDefault()
   onSend()
  }
 }

 return (
  <main className="chat-area">
   <div className="messages-container">
    {messages.length === 0 ? (
     <WelcomeScreen
      onSuggestionClick={onSuggestionClick}
      initialCategory={initialCategory}
     />
    ) : (
     messages.map((msg, idx) => (
      <div key={idx} className={`message-wrapper ${msg.role}`}>
       <Message message={msg} onQuestionClick={onSuggestionClick} />

       {msg.products?.length > 0 && (
        <ProductGrid products={msg.products} />
       )}

       {msg.avoidedKeywords?.length > 0 && (
        <div className="filtered-notice">
         <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M22 3l-8.646 8.646M16 3h6v6M8 11l-6 6M14.5 3L3 14.5" />
         </svg>
         Filtered out: {msg.avoidedKeywords.join(', ')}
        </div>
       )}
      </div>
     ))
    )}

    {isLoading && (
     <div className="message-wrapper assistant">
      <div className="message-bubble loading">
       <div className="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
       </div>
       <span className="typing-text">Searching products...</span>
      </div>
     </div>
    )}

    <div ref={messagesEndRef} />
   </div>

   {/* Input Area */}
   <div className="input-area">
    <div className="input-container">
     <input
      type="text"
      value={input}
      onChange={(e) => onInputChange(e.target.value)}
      onKeyPress={handleKeyPress}
      placeholder="Describe what you're looking for..."
      disabled={isLoading}
     />
     <button
      onClick={onSend}
      disabled={isLoading || !input.trim()}
      className="send-btn"
      aria-label="Send message"
     >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
       <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
      </svg>
     </button>
    </div>
    <p className="input-hint">
     Tip: Say "avoid chunky" or "no oversized" to filter styles
    </p>
   </div>
  </main>
 )
}

export default ChatArea
