import ThemeProvider from '@/context/ThemeContext'
import AuthProvider from '@/context/AuthContext'
import ToastProvider from '@/context/ToastContext'
import AppRoutes from '@/routes'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          <AppRoutes />
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
