"""
AI Model Analysis System

Uses AI to analyze Hugging Face models and provide comprehensive scoring
across multiple quality dimensions in a single call.
"""

import json
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from gateway import AIGateway
from hugging_face_api import get_model_info
from license_sub_score import fetch_readme


class AIModelAnalyzer:
    """AI-powered model analyzer that scores Hugging Face models"""
    
    def __init__(self, gateway_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI model analyzer
        
        Args:
            gateway_config: Configuration for AI gateway (optional)
        """
        self.gateway = AIGateway(gateway_config)
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load the AI scoring prompt from markdown file"""
        prompt_path = Path(__file__).parent / "ai_scoring_prompt.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
    
    def _gather_model_data(self, model_id: str) -> Dict[str, Any]:
        """
        Gather all necessary data about a model from Hugging Face
        
        Args:
            model_id: Hugging Face model ID (e.g., "microsoft/CodeBERT-base")
            
        Returns:
            Dictionary containing model metadata and README content
        """
        print(f"Gathering data for model: {model_id}")
        
        # Get model info from Hugging Face API
        model_info, api_time = get_model_info(model_id)
        if not model_info:
            raise ValueError(f"Could not fetch model info for {model_id}")
        
        # Get README content
        readme_content = fetch_readme(model_id)
        
        # Prepare data for AI analysis
        model_data = {
            "model_id": model_id,
            "metadata": {
                "id": model_info.get("id", ""),
                "author": model_info.get("author", ""),
                "downloads": model_info.get("downloads", 0),
                "likes": model_info.get("likes", 0),
                "tags": model_info.get("tags", []),
                "library_name": model_info.get("library_name", ""),
                "cardData": model_info.get("cardData", {})
            },
            "readme_content": readme_content or "",
            "api_fetch_time": api_time
        }
        
        return model_data
    
    def _create_analysis_prompt(self, model_data: Dict[str, Any]) -> str:
        """
        Create the complete prompt for AI analysis
        
        Args:
            model_data: Model data gathered from Hugging Face
            
        Returns:
            Complete prompt string for AI
        """
        # Format the model data for the AI
        data_summary = f"""
## Model Data for Analysis

**Model ID**: {model_data['model_id']}

**Metadata**:
- Downloads: {model_data['metadata']['downloads']:,}
- Likes: {model_data['metadata']['likes']}
- Author: {model_data['metadata']['author']}
- Tags: {', '.join(model_data['metadata']['tags'])}
- Library: {model_data['metadata']['library_name']}
- License: {model_data['metadata']['cardData'].get('license', 'Not specified')}

**README Content**:
```
{model_data['readme_content'][:2000]}{'...' if len(model_data['readme_content']) > 2000 else ''}
```

Please analyze this model and provide your scoring in the exact JSON format specified in the instructions.
"""
        
        return self.prompt_template + "\n\n" + data_summary
    
    def analyze_model(self, model_id: str, provider: str = "purdue", model: str = "llama3.1:latest") -> Dict[str, Any]:
        """
        Analyze a Hugging Face model using AI
        
        Args:
            model_id: Hugging Face model ID
            provider: AI provider to use (default: "purdue")
            model: AI model to use (default: "llama3.1:latest")
            
        Returns:
            Dictionary containing scores and analysis
        """
        start_time = time.time()
        
        try:
            # Gather model data
            model_data = self._gather_model_data(model_id)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(model_data)
            
            # Send to AI for analysis
            print(f"Sending analysis request to {provider} ({model})...")
            ai_response = self.gateway.chat(prompt, provider=provider, model=model)
            
            # Parse AI response
            analysis_result = self._parse_ai_response(ai_response)
            
            # Add metadata
            analysis_result["model_id"] = model_id
            analysis_result["analysis_time"] = time.time() - start_time
            analysis_result["ai_provider"] = provider
            analysis_result["ai_model"] = model
            
            return analysis_result
            
        except Exception as e:
            return {
                "error": str(e),
                "model_id": model_id,
                "analysis_time": time.time() - start_time
            }
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the AI response and extract JSON data
        
        Args:
            response: Raw AI response string
            
        Returns:
            Parsed analysis data
        """
        try:
            # Look for JSON in the response
            # Try to find JSON block between ```json and ```
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end != -1:
                    json_str = response[start:end].strip()
                else:
                    # Fallback: look for JSON-like content
                    json_str = response[start:].strip()
            else:
                # Try to find JSON object in the response
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                else:
                    raise ValueError("No JSON found in AI response")
            
            # Parse JSON
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["bus_factor", "ramp_up_time", "performance_claims", "license", "dataset_quality", "net_score", "summary"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from AI response: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse AI response: {e}")


def analyze_model_with_ai(model_id: str, gateway_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze a model with AI
    
    Args:
        model_id: Hugging Face model ID
        gateway_config: Optional gateway configuration
        
    Returns:
        Analysis results dictionary
    """
    analyzer = AIModelAnalyzer(gateway_config)
    return analyzer.analyze_model(model_id)


# Example usage and testing
if __name__ == "__main__":
    # Test with a sample model
    test_model = "microsoft/CodeBERT-base"
    
    print("=" * 60)
    print("AI MODEL ANALYSIS SYSTEM")
    print("=" * 60)
    print(f"Testing with model: {test_model}")
    print()
    
    try:
        # Initialize analyzer
        analyzer = AIModelAnalyzer()
        
        # Analyze the model
        result = analyzer.analyze_model(test_model)
        
        if "error" in result:
            print(f"❌ Analysis failed: {result['error']}")
        else:
            print("✅ Analysis completed successfully!")
            print()
            print("SCORES:")
            print(f"  Bus Factor: {result['bus_factor']}/10")
            print(f"  Ramp-up Time: {result['ramp_up_time']:.2f}")
            print(f"  Performance Claims: {result['performance_claims']:.2f}")
            print(f"  License: {result['license']:.2f}")
            print(f"  Dataset Quality: {result['dataset_quality']:.2f}")
            print(f"  Net Score: {result['net_score']:.2f}")
            print()
            print("SUMMARY:")
            print(f"  {result['summary']}")
            print()
            print(f"Analysis completed in {result['analysis_time']:.2f} seconds")
            print(f"AI Provider: {result['ai_provider']} ({result['ai_model']})")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. PURDUE_API_KEY set in your environment or .env file")
        print("2. Internet connection for Hugging Face API calls")
        print("3. The ai_scoring_prompt.md file in the same directory")
