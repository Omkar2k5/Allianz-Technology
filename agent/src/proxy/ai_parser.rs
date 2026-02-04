use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct AIRequestData {
    pub model: String,
    pub prompt: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AIResponseData {
    pub model: String,
    pub prompt_tokens: i32,
    pub completion_tokens: i32,
    pub total_tokens: i32,
}

/// Parse OpenAI-compatible request body
pub fn parse_ai_request(body: &str) -> Option<AIRequestData> {
    let json: serde_json::Value = serde_json::from_str(body).ok()?;
    
    // Extract model (ChatGPT uses "model" field)
    let model = json.get("model")
        .and_then(|m| m.as_str())
        .unwrap_or("unknown")
        .to_string();
    
    // Extract prompt from various possible fields
    let prompt = if let Some(messages) = json.get("messages").and_then(|m| m.as_array()) {
        // OpenAI chat format
        messages.iter()
            .filter_map(|msg| msg.get("content").and_then(|c| c.as_str()))
            .collect::<Vec<_>>()
            .join(" ")
    } else if let Some(prompt_str) = json.get("prompt").and_then(|p| p.as_str()) {
        // Completion format
        prompt_str.to_string()
    } else if let Some(content) = json.get("content").and_then(|c| c.as_str()) {
        // ChatGPT web format
        content.to_string()
    } else {
        "".to_string()
    };
    
    Some(AIRequestData { model, prompt })
}

/// Parse OpenAI-compatible response body
pub fn parse_ai_response(body: &str) -> Option<AIResponseData> {
    // Try standard JSON format first
    if let Ok(json) = serde_json::from_str::<serde_json::Value>(body) {
        // Extract usage data
        if let Some(usage) = json.get("usage") {
            let model = json.get("model")
                .and_then(|m| m.as_str())
                .unwrap_or("unknown")
                .to_string();
            
            let prompt_tokens = usage.get("prompt_tokens")
                .and_then(|t| t.as_i64())
                .unwrap_or(0) as i32;
            
            let completion_tokens = usage.get("completion_tokens")
                .and_then(|t| t.as_i64())
                .unwrap_or(0) as i32;
            
            let total_tokens = usage.get("total_tokens")
                .and_then(|t| t.as_i64())
                .unwrap_or(prompt_tokens as i64 + completion_tokens as i64) as i32;
            
            return Some(AIResponseData {
                model,
                prompt_tokens,
                completion_tokens,
                total_tokens,
            });
        }
    }
    
    // Try ChatGPT SSE format (Server-Sent Events)
    // The response might be gzip-compressed, try to decompress first
    let decompressed = try_decompress_gzip(body.as_bytes());
    let text_to_parse = if let Some(ref dec) = decompressed {
        dec.as_str()
    } else {
        body
    };
    
    // Debug: check if "usage" appears anywhere in the response
    if text_to_parse.contains("usage") {
        // Find the position and extract context
        if let Some(pos) = text_to_parse.find("usage") {
            let start = pos.saturating_sub(100);
            let end = (pos + 200).min(text_to_parse.len());
            tracing::debug!("Found 'usage' in response at position {}: {}", pos, &text_to_parse[start..end]);
        }
    }
    
    // Split into SSE frames (separated by \r\n\r\n or \n\n)
    let frames: Vec<&str> = text_to_parse.split("\r\n\r\n")
        .chain(text_to_parse.split("\n\n"))
        .collect();
    
    for frame in frames {
        // Extract all data: lines
        let data_lines: Vec<&str> = frame
            .lines()
            .filter(|line| line.starts_with("data: "))
            .map(|line| line.strip_prefix("data: ").unwrap_or(""))
            .collect();
        
        if data_lines.is_empty() {
            continue;
        }
        
        let data_joined = data_lines.join("\n");
        if data_joined.trim() == "[DONE]" {
            continue;
        }
        
        // Try to parse as JSON
        if let Ok(json) = serde_json::from_str::<serde_json::Value>(&data_joined) {
            // Look for usage in response.usage or message.usage
            let usage = json.get("response")
                .and_then(|r| r.get("usage"))
                .or_else(|| json.get("message").and_then(|m| m.get("usage")))
                .or_else(|| json.get("usage"));
            
            if let Some(usage_obj) = usage {
                let model = json.get("response")
                    .and_then(|r| r.get("message"))
                    .and_then(|m| m.get("metadata"))
                    .and_then(|m| m.get("model_slug"))
                    .and_then(|m| m.as_str())
                    .or_else(|| json.get("model").and_then(|m| m.as_str()))
                    .unwrap_or("unknown")
                    .to_string();
                
                let prompt_tokens = usage_obj.get("prompt_tokens")
                    .or_else(|| usage_obj.get("input_tokens"))
                    .and_then(|t| t.as_i64())
                    .unwrap_or(0) as i32;
                
                let completion_tokens = usage_obj.get("completion_tokens")
                    .or_else(|| usage_obj.get("output_tokens"))
                    .and_then(|t| t.as_i64())
                    .unwrap_or(0) as i32;
                
                let total_tokens = usage_obj.get("total_tokens")
                    .and_then(|t| t.as_i64())
                    .unwrap_or(prompt_tokens as i64 + completion_tokens as i64) as i32;
                
                return Some(AIResponseData {
                    model,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                });
            }
        }
    }
    
    None
}

/// Try to decompress gzip data
fn try_decompress_gzip(data: &[u8]) -> Option<String> {
    use std::io::Read;
    use flate2::read::GzDecoder;
    
    let mut decoder = GzDecoder::new(data);
    let mut decompressed = String::new();
    
    match decoder.read_to_string(&mut decompressed) {
        Ok(_) => Some(decompressed),
        Err(_) => None,
    }
}

/// Check if URI path is an AI completion endpoint
pub fn is_ai_completion_endpoint(path: &str) -> bool {
    path.contains("/chat/completions") 
        || path.contains("/completions")
        || path.contains("/v1/messages")  // Anthropic
        || path.contains("/generate")     // Generic
        || path.contains("/backend-api/conversation")  // ChatGPT web interface (all conversation endpoints)
        || path.contains("/backend-api/f/conversation")  // ChatGPT conversation flow
        || path.contains("/api/chat")     // Generic chat API
}
