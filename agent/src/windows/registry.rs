

#[cfg(target_os = "windows")]
use windows::Win32::System::Registry::*;
#[cfg(target_os = "windows")]
use windows::core::PCSTR;
use anyhow::Result;
use tracing::{info, warn};

#[cfg(target_os = "windows")]
pub fn set_system_proxy(enable: bool, addr: &str) -> Result<()> {
    unsafe {
        let key_path = "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\0";
        let mut key: HKEY = std::mem::zeroed();
        
        let result = RegOpenKeyExA(
            HKEY_CURRENT_USER,
            PCSTR(key_path.as_ptr()),
            0,
            KEY_WRITE,
            &mut key,
        );

        if result.is_err() {
            warn!("Failed to open registry key");
            return Ok(());
        }

        if enable {
            // Enable proxy
            let proxy_enable: u32 = 1;
            let _ = RegSetValueExA(
                key,
                PCSTR("ProxyEnable\0".as_ptr()),
                0,
                REG_DWORD,
                Some(&proxy_enable.to_le_bytes()),
            );

            // Set proxy server
            let proxy_server = format!("{}\0", addr);
            let _ = RegSetValueExA(
                key,
                PCSTR("ProxyServer\0".as_ptr()),
                0,
                REG_SZ,
                Some(proxy_server.as_bytes()),
            );

            info!("✅ System proxy enabled: {}", addr);
        } else {
            // Disable proxy
            let proxy_enable: u32 = 0;
            let _ = RegSetValueExA(
                key,
                PCSTR("ProxyEnable\0".as_ptr()),
                0,
                REG_DWORD,
                Some(&proxy_enable.to_le_bytes()),
            );

            info!("✅ System proxy disabled");
        }

        let _ = RegCloseKey(key);
    }

    Ok(())
}

#[cfg(not(target_os = "windows"))]
pub fn set_system_proxy(_enable: bool, _addr: &str) -> Result<()> {
    warn!("System proxy configuration only supported on Windows");
    Ok(())
}
