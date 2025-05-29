import requests
import json
from typing import Dict, List, Optional

class OllamaIntegration:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "codellama"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
    
    def get_suggestions(self, code: str, analysis_context: Dict) -> Dict:
        """
        Get AI suggestions for code improvements
        """
        try:
            prompt = self._build_prompt(code, analysis_context)
            response = self._call_ollama_api(prompt)
            return {
                "suggestions": response,
                "status": "success"
            }
        except Exception as e:
            return {
                "suggestions": f"Error getting suggestions: {str(e)}",
                "status": "error"
            }
    
    def _build_prompt(self, code: str, context: Dict) -> str:
        """
        Build a prompt for the AI model
        """
        prompt = f"""
Analyze the following Python code and provide suggestions for improvement:

Code:
{code}

Context:
- Issues found: {context.get('issues', [])}
- Complexity score: {context.get('complexity_score', 'N/A')}
- Performance issues: {context.get('performance_issues', [])}

Please provide:
1. Specific improvement suggestions
2. Code quality recommendations
3. Performance optimizations
4. Best practices violations

Respond in a clear, structured format.
"""
        return prompt
    
    def _call_ollama_api(self, prompt: str) -> str:
        """
        Make API call to Ollama
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response received')
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure Ollama is running on localhost:11434"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model might be loading."
        except Exception as e:
            return f"Error: {str(e)}"