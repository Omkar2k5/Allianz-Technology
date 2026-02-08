import { API_URL } from '@/config'

export default function SignUpPage() {
    const navigate = useNavigate()
    const [firstName, setFirstName] = useState('')
    const [lastName, setLastName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [team, setTeam] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)
        setError('')

        try {
            const res = await fetch(`${API_URL}/api/v1/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    email,
                    password,
                    team_name: team || undefined
                }),
            })

            const data = await res.json()

            if (!res.ok) {
                throw new Error(data.detail || 'Failed to sign up')
            }

            // Store token
            localStorage.setItem('token', data.access_token)
            localStorage.setItem('refresh_token', data.refresh_token)
            localStorage.setItem('user', JSON.stringify(data.user))

            // Redirect
            navigate('/dashboard')
        } catch (err: any) {
            setError(err.message)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4 py-8">
            <div className="w-full max-w-md">
                <Card className="border-0 shadow-lg">
                    <div className="p-8">
                        {/* Logo */}
                        <div className="flex items-center justify-center mb-8">
                            <div className="flex items-center gap-2">
                                <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                                    <Leaf className="w-6 h-6 text-primary-foreground" />
                                </div>
                                <span className="text-xl font-bold text-foreground">Eco-Compute</span>
                            </div>
                        </div>

                        {/* Heading */}
                        <h1 className="text-2xl font-bold text-center mb-2 text-foreground">Sign up</h1>
                        <p className="text-center text-muted-foreground mb-8">
                            Start tracking your AI carbon footprint today
                        </p>

                        {/* Error Message */}
                        {error && (
                            <div className="bg-destructive/15 text-destructive text-sm p-3 rounded-md mb-6">
                                {error}
                            </div>
                        )}

                        {/* Form */}
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <Label htmlFor="firstName" className="text-sm font-medium">First Name</Label>
                                    <Input
                                        id="firstName"
                                        value={firstName}
                                        onChange={(e) => setFirstName(e.target.value)}
                                        className="mt-2"
                                        required
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="lastName" className="text-sm font-medium">Last Name</Label>
                                    <Input
                                        id="lastName"
                                        value={lastName}
                                        onChange={(e) => setLastName(e.target.value)}
                                        className="mt-2"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <Label htmlFor="email" className="text-sm font-medium">Email address</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="you@company.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="mt-2"
                                    required
                                />
                            </div>

                            <div>
                                <Label htmlFor="password" className="text-sm font-medium">Password</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="mt-2"
                                    required
                                />
                            </div>

                            <div>
                                <Label htmlFor="team" className="text-sm font-medium">Team Name (Optional)</Label>
                                <Input
                                    id="team"
                                    placeholder="e.g. Data Science Team"
                                    value={team}
                                    onChange={(e) => setTeam(e.target.value)}
                                    className="mt-2"
                                />
                            </div>

                            <Button
                                type="submit"
                                disabled={isLoading}
                                className="w-full h-10 bg-primary text-primary-foreground hover:bg-primary/90 mt-6"
                            >
                                {isLoading ? 'Creating account...' : 'Create account'}
                            </Button>
                        </form>

                        {/* Footer */}
                        <p className="text-center text-sm text-muted-foreground mt-6">
                            Already have an account?{' '}
                            <Link to="/login" className="text-primary hover:underline font-medium">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </Card>
            </div>
        </div>
    )
}
