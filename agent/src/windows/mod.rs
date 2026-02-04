"""
Windows-specific integrations
"""

#[cfg(target_os = "windows")]
pub mod registry;

#[cfg(not(target_os = "windows"))]
pub mod registry {
    use anyhow::Result;
    
    pub fn set_system_proxy(_enable: bool, _addr: &str) -> Result<()> {
        Ok(())
    }
}
