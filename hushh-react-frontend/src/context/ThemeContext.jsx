import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export const useTheme = () => {
 const context = useContext(ThemeContext)
 if (!context) {
  throw new Error('useTheme must be used within a ThemeProvider')
 }
 return context
}

export const ThemeProvider = ({ children }) => {
 const [isDark, setIsDark] = useState(() => {
  const saved = localStorage.getItem('hushh-theme')
  return saved ? saved === 'dark' : true // Default to dark
 })

 useEffect(() => {
  localStorage.setItem('hushh-theme', isDark ? 'dark' : 'light')
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
 }, [isDark])

 const toggleTheme = () => setIsDark(prev => !prev)

 return (
  <ThemeContext.Provider value={{ isDark, toggleTheme }}>
   {children}
  </ThemeContext.Provider>
 )
}
