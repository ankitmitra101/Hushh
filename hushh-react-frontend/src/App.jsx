import { useState, useRef, useEffect } from 'react'
import { ThemeProvider } from './context/ThemeContext'
import LandingPage from './components/LandingPage'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import './App.css'

// Use environment variable or fallback to Render backend
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://hushh-backend-uc5w.onrender.com'
const API_URL = `${BACKEND_URL}/agents/run`
const HEALTH_URL = `${BACKEND_URL}/health`
const CLEAR_URL = `${BACKEND_URL}/agents/clear`

// Generate a unique session ID
const generateSessionId = () => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

function AppContent() {
  const [currentPage, setCurrentPage] = useState('landing')
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [avoidKeywords, setAvoidKeywords] = useState([])
  const [sessionData, setSessionData] = useState({})
  const [backendStatus, setBackendStatus] = useState('checking')
  const [userId, setUserId] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [lastApiResponse, setLastApiResponse] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    const initializeSession = async () => {
      // DEBUG: Force fresh user ID every time to avoid stale memory
      const newUserId = `debug_user_${Date.now()}`
      localStorage.setItem('hushh_user_id', newUserId)
      setUserId(newUserId)

      const newSessionId = `session_${Date.now()}`
      setSessionId(newSessionId)

      console.log('Initialized Session:', { userId: newUserId, newSessionId })

      // Warm up backend
      try {
        await fetch(`${import.meta.env.VITE_BACKEND_URL}/health`)
      } catch (e) {
        console.log('Backend waking up...')
      }
      checkBackend() // Also check backend status
    }
    initializeSession()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const checkBackend = async () => {
    setBackendStatus('checking')
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000)

      const response = await fetch(HEALTH_URL, { signal: controller.signal })
      clearTimeout(timeoutId)

      setBackendStatus(response.ok ? 'online' : 'offline')
    } catch {
      setBackendStatus('offline')
    }
  }

  const handleGetStarted = (category) => {
    setSelectedCategory(category)
    setCurrentPage('chat')
  }

  const handleBackToLanding = async () => {
    // Clear conversation on backend before going back
    try {
      await fetch(CLEAR_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      })
    } catch (e) {
      console.log('Could not clear conversation on backend')
    }

    // Reset all state and generate new session
    setCurrentPage('landing')
    setMessages([])
    setSessionData({})
    setAvoidKeywords([])
    setSelectedCategory(null)
    setSessionId(generateSessionId())  // New session for next chat
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: `guest_${sessionId}`, // Use unique ID to prevent old memory persistence
          message: userMessage,
          session_id: sessionId  // Send session ID for conversation tracking
        })
      })

      const data = await response.json()
      setLastApiResponse(data)
      console.log('=== API RESPONSE ===', JSON.stringify(data, null, 2))

      const understood = data.understood_request || {}
      const constraints = understood.constraints || {}
      const products = data.results || []
      console.log('Parsed Products:', products.length)

      const questions = data.clarifying_questions || []

      setSessionData({
        category: constraints.category || understood.category,
        budget: constraints.budget_inr_max,
        size: constraints.size,
        styleKeywords: constraints.style_keywords || []
      })

      if (constraints.avoid_keywords?.length) {
        setAvoidKeywords(prev => [...new Set([...prev, ...constraints.avoid_keywords])])
      }

      let responseContent = ''
      if (data.error) {
        responseContent = `Something went wrong: ${data.error}`
      } else if (products.length > 0) {
        responseContent = `Found ${products.length} matches for you.`
      } else {
        // Always show this - don't ask questions
        responseContent = 'No products found matching your search. Try a different query.'
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: responseContent,
        products,
        questions,
        avoidedKeywords: constraints.avoid_keywords || []
      }])

    } catch (error) {
      console.error('API Error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Connection issue. The backend might be starting up - please try again.'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = (text) => {
    setInput(text)
  }

  const removeAvoidKeyword = (keyword) => {
    setAvoidKeywords(prev => prev.filter(k => k !== keyword))
  }

  const clearChat = async () => {
    // Clear on backend
    try {
      await fetch(CLEAR_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      })
    } catch (e) {
      console.log('Could not clear conversation on backend')
    }

    // Clear frontend state but keep same session
    setMessages([])
    setSessionData({})
    setAvoidKeywords([])
    setSessionId(generateSessionId())  // New session
  }

  // Show Landing Page
  if (currentPage === 'landing') {
    return <LandingPage onGetStarted={handleGetStarted} />
  }

  // Show Chat Interface
  return (
    <div className="app">
      <Header
        backendStatus={backendStatus}
        onTestConnection={checkBackend}
        onBack={handleBackToLanding}
        showBack={true}
      />

      <div className="main-layout">
        <Sidebar
          userName="Ankit"
          userId="ankit_01"
          avoidKeywords={avoidKeywords}
          sessionData={sessionData}
          onRemoveKeyword={removeAvoidKeyword}
          onClearChat={clearChat}
        />

        <ChatArea
          messages={messages}
          isLoading={isLoading}
          input={input}
          onInputChange={setInput}
          onSend={sendMessage}
          onSuggestionClick={handleSuggestionClick}
          messagesEndRef={messagesEndRef}
          initialCategory={selectedCategory}
        />
      </div>
    </div>
  )
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  )
}

export default App
