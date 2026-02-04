

pub struct AIDetector {
    domains: Vec<String>,
}

impl AIDetector {
    pub fn new() -> Self {
        Self {
            domains: vec![
                "api.openai.com".to_string(),
                "openai.com".to_string(),
                "chatgpt.com".to_string(),
                "api.anthropic.com".to_string(),
                "claude.ai".to_string(),
                "openrouter.ai".to_string(),
                "api.cohere.ai".to_string(),
                "generativelanguage.googleapis.com".to_string(),
            ],
        }
    }

    pub fn is_ai_request(&self, host: &str, path: &str) -> bool {
        let is_ai_domain = self.domains.iter().any(|domain| host.contains(domain));
        
        // If path is empty (CONNECT request), only check domain
        if path.is_empty() {
            return is_ai_domain;
        }

        let is_ai_path = path.contains("/v1/chat/completions") 
            || path.contains("/v1/completions")
            || path.contains("/v1/embeddings")
            || path.contains("/messages")
            || path.contains("backend-api"); // ChatGPT internal API
        
        is_ai_domain && is_ai_path
    }
}

impl Default for AIDetector {
    fn default() -> Self {
        Self::new()
    }
}
