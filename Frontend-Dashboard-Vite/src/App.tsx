import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from '@/components/DashboardLayout'
import SignInPage from '@/pages/auth/Login'
import SignUpPage from '@/pages/auth/Signup'
import Dashboard from '@/pages/dashboard/Dashboard'
import Energy from '@/pages/dashboard/Energy'
import Usage from '@/pages/dashboard/Usage'
import RFE from '@/pages/dashboard/RFE'
import Recommendations from '@/pages/dashboard/Recommendations'

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/login" element={<SignInPage />} />
                <Route path="/signup" element={<SignUpPage />} />

                {/* Protected Dashboard Routes */}
                <Route path="/" element={<DashboardLayout />}>
                    <Route index element={<Navigate to="/dashboard" replace />} />
                    <Route path="dashboard" element={<Dashboard />} />
                    <Route path="energy" element={<Energy />} />
                    <Route path="usage" element={<Usage />} />
                    <Route path="rfe" element={<RFE />} />
                    <Route path="recommendations" element={<Recommendations />} />
                </Route>
            </Routes>
        </Router>
    )
}


export default App
