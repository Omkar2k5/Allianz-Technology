# Testing the Eco-Compute Agent

## ⚠️ IMPORTANT: Current Status

The agent now has **basic HTTP proxy forwarding** implemented. This means:
- ✅ The proxy will forward HTTP traffic correctly
- ✅ Internet connectivity will work when the proxy is enabled
- ✅ Graceful shutdown (Ctrl+C) will disable the Windows proxy
- ⚠️ **HTTPS traffic is NOT yet supported** - HTTPS sites will fail
- ⚠️ AI request logging is not yet implemented (detection hooks are in place)
- ⚠️ Authentication is not yet implemented

## Before Testing

**IMPORTANT**: Make sure you can manually disable the Windows proxy if something goes wrong:

1. Open Windows Settings
2. Go to Network & Internet → Proxy
3. Toggle "Use a proxy server" to OFF if needed

## Running the Agent

### Option 1: Debug Mode (with logs)
```powershell
cd "c:\Projects\Allianz Technology\agent"
cargo run
```

### Option 2: Release Mode (faster)
```powershell
cd "c:\Projects\Allianz Technology\agent"
.\target\release\ecocompute-agent.exe
```

## What to Expect

When you run the agent, you should see:
```
🚀 Eco-Compute Agent starting...
Version: 0.1.0
✅ Configuration loaded
✅ Local database table created/verified
✅ Local database initialized
✅ System proxy enabled: 127.0.0.1:8080
✅ System proxy configured: 127.0.0.1:8080
🌐 Starting proxy server on 127.0.0.1:8080...
✅ Proxy server listening on 127.0.0.1:8080
🌐 Proxy server started successfully
```

## Testing HTTP Traffic

### Test 1: Basic HTTP Request
Open a new PowerShell window and run:
```powershell
curl http://example.com
```

**Expected**: You should see the HTML content of example.com

### Test 2: Check Proxy is Working
```powershell
# Check Windows proxy settings
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" | Select-Object ProxyEnable, ProxyServer
```

**Expected**: 
- ProxyEnable: 1
- ProxyServer: 127.0.0.1:8080

### Test 3: AI Request Detection (HTTP only)
The agent will log when it detects AI API requests. Look for:
```
🤖 AI API request detected: api.openai.com /v1/chat/completions
```

## Stopping the Agent

Press `Ctrl+C` in the terminal where the agent is running.

You should see:
```
🛑 Shutdown signal received
✅ System proxy disabled
```

**Verify**: Check Windows proxy settings again - it should be disabled.

## Known Limitations

1. **HTTPS Not Supported Yet**: Most websites use HTTPS, so web browsing will be limited
2. **No AI Request Logging**: Detection works, but requests aren't logged to the database yet
3. **No Authentication**: The agent doesn't require login yet
4. **No Backend Sync**: Logs aren't sent to the backend yet

## Troubleshooting

### Internet Not Working
1. Press `Ctrl+C` to stop the agent
2. Manually disable proxy in Windows Settings
3. Check the agent logs for errors

### Agent Won't Start
- Check if port 8080 is already in use
- Check if another proxy is already configured
- Look at the error messages in the terminal

### Proxy Not Disabled on Exit
If the agent crashes and doesn't disable the proxy:
```powershell
# Manually disable proxy
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Value 0
```

## Next Steps

After verifying basic HTTP forwarding works, we'll implement:
1. HTTPS/TLS support (Phase 4)
2. Authentication flow (Phase 2)
3. AI request logging (Phase 3)
4. Backend synchronization (Phase 5)
