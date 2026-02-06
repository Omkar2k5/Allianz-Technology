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
    // Check if this is a Gemini request (URL-encoded with f.req parameter)
    if body.starts_with("f.req=") {
        return parse_gemini_request(body);
    }
    
    let json: serde_json::Value = serde_json::from_str(body).ok()?;
    
    // Extract model (ChatGPT uses "model" field)
    let model = json.get("model")
        .and_then(|m| m.as_str())
        .unwrap_or("unknown")
        .to_string();
    
    // Extract prompt from various possible fields
    let prompt = if let Some(messages) = json.get("messages").and_then(|m| m.as_array()) {
        // ChatGPT format: messages[].content.parts[]
        messages.iter()
            .filter_map(|msg| {
                msg.get("content")
                    .and_then(|content| {
                        // Try nested parts array first (ChatGPT web format)
                        if let Some(parts) = content.get("parts").and_then(|p| p.as_array()) {
                            Some(parts.iter()
                                .filter_map(|part| part.as_str())
                                .collect::<Vec<_>>()
                                .join(" "))
                        } else {
                            // Fallback to direct string content (OpenAI API format)
                            content.as_str().map(|s| s.to_string())
                        }
                    })
            })
            .collect::<Vec<_>>()
            .join(" ")
    } else if let Some(prompt_str) = json.get("prompt").and_then(|p| p.as_str()) {
        // Completion format
        prompt_str.to_string()
    } else if let Some(content) = json.get("content").and_then(|c| c.as_str()) {
        // Direct content format
        content.to_string()
    } else {
        "".to_string()
    };
    
    Some(AIRequestData { model, prompt })
}

/// Parse Gemini URL-encoded request
fn parse_gemini_request(body: &str) -> Option<AIRequestData> {
    // URL decode the body
    let decoded = urlencoding::decode(body).ok()?;
    
    // Extract the prompt - Gemini sends it in the f.req parameter as a nested JSON array
    // Look for text between quotes that looks like a user prompt
    // Simple heuristic: find text after "google" that's not a conversation ID
    let prompt = decoded
        .split("\\\"")
        .filter(|s| s.len() > 10 && !s.starts_with("c_") && !s.starts_with("r_") && !s.starts_with("rc_"))
        .find(|s| !s.contains("google") && !s.contains("en-IN") && !s.contains("Aw"))
        .unwrap_or("")
        .to_string();
    
    Some(AIRequestData {
        model: "gemini-pro".to_string(),
        prompt,
    })
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

pub fn is_ai_completion_endpoint(path: &str) -> bool {
    // Exclude known auxiliary/list endpoints
    if path.contains("/conversations")  // List endpoint (plural)
        || path.contains("/init") 
        || path.contains("/stream_status") 
        || path.contains("/textdocs")
        || path.contains("/generate_autocompletions")
        || path.contains("/prepare")  // ChatGPT preparation endpoints
        || path.contains("/finalize") // ChatGPT finalization endpoints
        || path.contains("/ces/v1/")  // ChatGPT telemetry
        || path.contains("/rgstr")    // ChatGPT registration
        || path.contains("/lat/r")    // ChatGPT latency reporting
        || path.contains("/links/list") // ChatGPT links
        || path.contains("/sentinel/") // ChatGPT sentinel/requirements
        || path.contains("/jserror")  // Gemini JS errors
        || path.contains("/cspreport") // Gemini CSP reports
        || path.contains("/batchexecute") { // Gemini batch operations
        return false;
    }

    // Only match specific conversation endpoints with actual prompts
    path.contains("/chat/completions") 
        || path.contains("/completions")
        || path.contains("/v1/messages")  // Anthropic
        || path.contains("/backend-api/f/conversation")  // ChatGPT main prompt endpoint
        || path.contains("/backend-api/conversation/")   // ChatGPT conversation with UUID
        || path.contains("/api/chat")     // Generic chat API
        || path.contains("/StreamGenerate") // Gemini prompt endpoint
}
