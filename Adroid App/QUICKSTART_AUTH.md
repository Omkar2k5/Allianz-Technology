# Quick Start Guide - Android Authentication

## 🚀 Getting Started

### 1. Configure Backend Server

Open [Constants.kt](file:///c:/Projects/Allianz%20Technology/Adroid%20App/app/src/main/java/com/example/eco_compute/utils/Constants.kt) and update the base URL:

```kotlin
const val BASE_URL = "http://YOUR_SERVER_IP:8000"
```

**Examples:**
- **Android Emulator**: `http://10.0.2.2:8000` (already configured)
- **Physical Device**: `http://192.168.1.100:8000` (replace with your IP)
- **Production**: `https://api.ecocompute.com`

### 2. Find Your Server IP

**Windows:**
```powershell
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

**Backend must be running:**
```bash
cd backend/analytics-api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Build and Run

**Option A: Android Studio**
1. Open the project in Android Studio
2. Wait for Gradle sync to complete
3. Click "Run" (green play button)
4. Select emulator or connected device

**Option B: Command Line**
```bash
cd "Adroid App"
./gradlew installDebug
```

---

## 📱 Testing the App

### Registration Flow
1. App opens → Splash screen (2 seconds)
2. Navigates to Login screen
3. Click "Sign Up"
4. Fill in:
   - First Name: `John`
   - Last Name: `Doe`
   - Email: `john.doe@example.com`
   - Password: `password123` (min 8 chars)
   - Confirm Password: `password123`
5. Click "Sign Up"
6. Should navigate to Dashboard automatically

### Login Flow
1. Click logout (top-right icon)
2. Enter credentials:
   - Email: `john.doe@example.com`
   - Password: `password123`
3. Click "Login"
4. Should navigate to Dashboard

### Token Persistence
1. Login successfully
2. Close app completely (swipe away from recents)
3. Reopen app
4. Should go directly to Dashboard (auto-login)

---

## 🐛 Troubleshooting

### "Network error" or "Unable to connect"

**Check:**
1. Backend is running: `http://YOUR_IP:8000/health`
2. Firewall allows port 8000
3. Device/emulator can reach server:
   ```bash
   # From device/emulator terminal
   ping YOUR_SERVER_IP
   ```

### "Email already registered"
- Email is already in database
- Use a different email or check backend database

### Build errors
```bash
cd "Adroid App"
./gradlew clean
./gradlew build
```

---

## 📝 Key Files to Know

| File | Purpose | When to Edit |
|------|---------|--------------|
| [Constants.kt](file:///c:/Projects/Allianz%20Technology/Adroid%20App/app/src/main/java/com/example/eco_compute/utils/Constants.kt) | API configuration | Change server IP |
| [network_security_config.xml](file:///c:/Projects/Allianz%20Technology/Adroid%20App/app/src/main/res/xml/network_security_config.xml) | HTTP/HTTPS settings | Switch to HTTPS |
| [LoginScreen.kt](file:///c:/Projects/Allianz%20Technology/Adroid%20App/app/src/main/java/com/example/eco_compute/ui/screens/LoginScreen.kt) | Login UI | Customize login screen |
| [SignupScreen.kt](file:///c:/Projects/Allianz%20Technology/Adroid%20App/app/src/main/java/com/example/eco_compute/ui/screens/SignupScreen.kt) | Signup UI | Customize signup screen |
| [DashboardScreen.kt](file:///c:/Projects/Allianz%20Technology/Adroid%20App/app/src/main/java/com/example/eco_compute/ui/screens/DashboardScreen.kt) | Main app screen | Add features |

---

## 🎯 What's Next?

### Immediate
- [ ] Configure backend IP in Constants.kt
- [ ] Test registration and login
- [ ] Verify token persistence

### Future Features
- [ ] Add "Forgot Password" flow
- [ ] Implement biometric authentication
- [ ] Add profile editing
- [ ] Implement token auto-refresh
- [ ] Add "Remember Me" option
- [ ] Email verification

---

## 📚 Architecture Overview

```
┌─────────────────────────────────────────┐
│           UI Layer (Compose)            │
│  LoginScreen, SignupScreen, Dashboard   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         ViewModels (State)              │
│  LoginViewModel, SignupViewModel        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Repository (Business Logic)        │
│         AuthRepository                  │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌─────▼──────┐
│  ApiService │  │TokenManager│
│  (Retrofit) │  │ (DataStore)│
└─────────────┘  └────────────┘
       │
┌──────▼──────────────────────────────────┐
│      Backend API (FastAPI)              │
│  /api/v1/auth/login, /register, etc.    │
└─────────────────────────────────────────┘
```

---

## 💡 Tips

- **Emulator**: Use `10.0.2.2` to access host machine's localhost
- **Physical Device**: Must be on same WiFi network as backend
- **HTTPS**: For production, update network security config
- **Debugging**: Check Logcat for detailed error messages
- **Backend Logs**: Check FastAPI console for request details
