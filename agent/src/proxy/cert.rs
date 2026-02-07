use anyhow::{Result, Context};
use rcgen::{Certificate, CertificateParams, DistinguishedName, DnType, IsCa, BasicConstraints, KeyUsagePurpose, ExtendedKeyUsagePurpose};
use std::fs;
use std::path::Path;
use tracing::info;

pub struct CertificateManager {
    root_cert: Certificate,
    root_cert_pem: String,
    _root_key_pem: String,
}

impl CertificateManager {
    pub fn new() -> Result<Self> {
        // Check if CA cert already exists
        if Path::new("ca_cert.pem").exists() && Path::new("ca_key.pem").exists() {
            info!("📜 Loading existing CA certificate from: {}", fs::canonicalize("ca_cert.pem")?.display());
            return Self::load_existing();
        }
        
        info!("🔐 Generating new CA certificate...");
        
        // Generate new CA certificate
        let mut params = CertificateParams::new(vec![]);
        params.distinguished_name = DistinguishedName::new();
        params.distinguished_name.push(DnType::CommonName, "Eco-Compute Root CA");
        params.distinguished_name.push(DnType::OrganizationName, "Eco-Compute");
        params.distinguished_name.push(DnType::CountryName, "US");
        params.is_ca = IsCa::Ca(BasicConstraints::Unconstrained);
        params.key_usages = vec![
            KeyUsagePurpose::KeyCertSign,
            KeyUsagePurpose::CrlSign,
        ];
        
        let cert = Certificate::from_params(params)
            .context("Failed to generate CA certificate")?;
        
        let cert_pem = cert.serialize_pem()
            .context("Failed to serialize certificate")?;
        let key_pem = cert.serialize_private_key_pem();
        
        // Save to disk
        fs::write("ca_cert.pem", &cert_pem)
            .context("Failed to write CA certificate")?;
        fs::write("ca_key.pem", &key_pem)
            .context("Failed to write CA private key")?;
        
        info!("✅ CA certificate generated and saved");
        
        Ok(Self {
            root_cert: cert,
            root_cert_pem: cert_pem,
            _root_key_pem: key_pem,
        })
    }
    
    fn load_existing() -> Result<Self> {
        let cert_pem = fs::read_to_string("ca_cert.pem")
            .context("Failed to read CA certificate")?;
        let key_pem = fs::read_to_string("ca_key.pem")
            .context("Failed to read CA private key")?;
        
        let key_pair = rcgen::KeyPair::from_pem(&key_pem)
            .context("Failed to parse CA private key")?;
        
        // Create params with the key pair
        let mut params = CertificateParams::new(vec![]);
        params.distinguished_name = DistinguishedName::new();
        params.distinguished_name.push(DnType::CommonName, "Eco-Compute Root CA");
        params.distinguished_name.push(DnType::OrganizationName, "Eco-Compute");
        params.distinguished_name.push(DnType::CountryName, "US");
        params.is_ca = IsCa::Ca(BasicConstraints::Unconstrained);
        params.key_usages = vec![
            KeyUsagePurpose::KeyCertSign,
            KeyUsagePurpose::CrlSign,
        ];
        params.key_pair = Some(key_pair);
        
        let cert = Certificate::from_params(params)
            .context("Failed to create certificate from params")?;
        
        Ok(Self {
            root_cert: cert,
            root_cert_pem: cert_pem,
            _root_key_pem: key_pem,
        })
    }
    
    pub fn generate_domain_cert(&self, domain: &str) -> Result<(String, String)> {
        // Generate certificate for specific domain
        let mut params = CertificateParams::new(vec![domain.to_string()]);
        params.distinguished_name = DistinguishedName::new();
        params.distinguished_name.push(DnType::CommonName, domain);
        // Add ServerAuth EKU which is required by modern browsers
        params.extended_key_usages = vec![ExtendedKeyUsagePurpose::ServerAuth];
        
        let cert = Certificate::from_params(params)
            .context("Failed to generate domain certificate")?;
        
        let cert_pem = cert.serialize_pem_with_signer(&self.root_cert)
            .context("Failed to sign domain certificate")?;
        let key_pem = cert.serialize_private_key_pem();
        
        Ok((cert_pem, key_pem))
    }
    
    pub fn get_root_cert_pem(&self) -> &str {
        &self.root_cert_pem
    }
}
