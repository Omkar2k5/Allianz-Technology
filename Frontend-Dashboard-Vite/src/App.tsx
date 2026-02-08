import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from '@/components/ProtectedRoute'
import DashboardLayout from '@/components/DashboardLayout'
import SignInPage from '@/pages/auth/Login'
import SignUpPage from '@/pages/auth/Signup'
import Dashboard from '@/pages/dashboard/Dashboard'
import Energy from '@/pages/dashboard/Energy'
import Usage from '@/pages/dashboard/Usage'
import Emissions from '@/pages/dashboard/Emissions'
import RFE from '@/pages/dashboard/RFE'
import Recommendations from '@/pages/dashboard/Recommendations'



import ReportsPage from '@/pages/dashboard/Reports'

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/login" element={<SignInPage />} />
                <Route path="/signup" element={<SignUpPage />} />

                {/* Protected Dashboard Routes */}
                <Route element={<ProtectedRoute />}>
                    <Route path="/" element={<DashboardLayout />}>
                        <Route index element={<Navigate to="/dashboard" replace />} />
                        <Route path="dashboard" element={<Dashboard />} />
                        <Route path="energy" element={<Energy />} />
                        <Route path="usage" element={<Usage />} />
                        <Route path="emissions" element={<Emissions />} />
                        <Route path="reports" element={<ReportsPage />} />
                        <Route path="rfe" element={<RFE />} />
                        <Route path="recommendations" element={<Recommendations />} />
                    </Route>
                </Route>
            </Routes>
        </Router>
    )
}


export default App
