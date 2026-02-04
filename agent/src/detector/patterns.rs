"""
AI API detection patterns
"""

pub struct AIDetector {
    domains: Vec<String>,
}

impl AIDetector {
    pub fn new() -> Self {
        Self {
            domains: vec![
                "api.openai.com".to_string(),
                "api.anthropic.com".to_string(),
                "openrouter.ai".to_string(),
                "api.cohere.ai".to_string(),
                "generativelanguage.googleapis.com".to_string(),
            ],
        }
    }

    pub fn is_ai_request(&self, host: &str, path: &str) -> bool {
        let is_ai_domain = self.domains.iter().any(|domain| host.contains(domain));
        let is_ai_path = path.contains("/v1/chat/completions") 
            || path.contains("/v1/completions")
            || path.contains("/v1/embeddings")
            || path.contains("/messages");
        
        is_ai_domain && is_ai_path
    }
}

impl Default for AIDetector {
    fn default() -> Self {
        Self::new()
    }
}
