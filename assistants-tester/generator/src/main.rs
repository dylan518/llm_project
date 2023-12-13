use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use reqwest;
use tokio;

// Your struct definitions
#[derive(Debug, Serialize, Clone)]
pub struct AssistantRequest {
    pub model: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub instructions: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tools: Option<Vec<HashMap<String, String>>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub file_ids: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<HashMap<String, String>>,
}

impl AssistantRequest {
    pub fn new(model: String) -> Self {
        Self {
            model,
            name: None,
            description: None,
            instructions: None,
            tools: None,
            file_ids: None,
            metadata: None,
        }
    }
}

// Other struct definitions...

// Main function to run the async code
#[tokio::main]
async fn main() {
    // Example: Sending a request to create a new assistant
    let assistant_request = AssistantRequest::new("model_name".to_string());
    
    // Replace with the actual API endpoint
    let url = "https://api.example.com/assistants";

    match create_assistant(url, &assistant_request).await {
        Ok(assistant) => println!("Created assistant: {:?}", assistant),
        Err(e) => eprintln!("Error creating assistant: {}", e),
    }
}

// Function to create an assistant
async fn create_assistant(url: &str, request: &AssistantRequest) -> Result<AssistantObject, reqwest::Error> {
    let client = reqwest::Client::new();
    let res = client.post(url)
                    .json(request)
                    .send()
                    .await?;

    // Parse the response JSON into the AssistantObject struct
    let assistant_object = res.json::<AssistantObject>().await?;
    Ok(assistant_object)
}

