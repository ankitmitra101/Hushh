import './Message.css'

const Message = ({ message, onQuestionClick }) => {
 return (
  <div className={`message-bubble ${message.role}`}>
   {message.role === 'assistant' && (
    <div className="message-avatar">
     <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z" />
     </svg>
    </div>
   )}

   <div className="message-text">
    <p>{message.content}</p>

    {/* Clarifying Questions */}
    {message.questions?.length > 0 && (
     <div className="question-list">
      {message.questions.map((q, idx) => (
       <button
        key={idx}
        className="question-btn"
        onClick={() => onQuestionClick(q)}
       >
        <span>{q}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
         <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
       </button>
      ))}
     </div>
    )}
   </div>
  </div>
 )
}

export default Message
