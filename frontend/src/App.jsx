import ThemeProvider from '@/context/ThemeContext'
import AuthProvider from '@/context/AuthContext'
import AppRoutes from '@/routes'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
