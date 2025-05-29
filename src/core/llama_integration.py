import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class RefactoringSuggestion:
    original_code: str
    suggested_code: str
    explanation: str
    confidence_score: float
    performance_impact: str

class LlamaRefactoringEngine:
    def __init__(self, model_endpoint: str, api_key: Optional[str] = None):
        self.model_endpoint = model_endpoint
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}' if api_key else None
        }
    
    def analyze_and_suggest(self, code_snippet: str, context: Dict) -> RefactoringSuggestion:
        """Use LLama model to analyze code and suggest improvements"""
        prompt = self._build_analysis_prompt(code_snippet, context)
        
        response = self._call_llama_model(prompt)
        return self._parse_llama_response(response, code_snippet)
    
    def _build_analysis_prompt(self, code: str, context: Dict) -> str:
        """Build prompt for LLama model analysis"""
        return f"""
        You are an expert in HECS (Hierarchical Entity Component System) architecture optimization.
        
        Analyze the following code snippet and provide refactoring suggestions:
        
        Code:
        ```
        {code}
        ```
        
        Context: {json.dumps(context, indent=2)}
        
        Please provide:
        1. Optimized version of the code
        2. Detailed explanation of improvements
        3. Expected performance impact
        4. Confidence score (0-1)
        
        Focus on:
        - Entity-component relationship optimization
        - System performance improvements
        - Memory usage reduction
        - Code maintainability
        
        Respond in JSON format with keys: optimized_code, explanation, performance_impact, confidence_score
        """
    
    def _call_llama_model(self, prompt: str) -> Dict:
        """Call LLama model API"""
        payload = {
            "model": "llama-2-70b-chat",
            "messages": [
                {"role": "system", "content": "You are an expert HECS architecture optimizer."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.model_endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"LLama API call failed: {e}")
    
    def _parse_llama_response(self, response: Dict, original_code: str) -> RefactoringSuggestion:
        """Parse LLama model response"""
        try:
            content = response['choices'][0]['message']['content']
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_content = content[start_idx:end_idx]
            
            parsed = json.loads(json_content)
            
            return RefactoringSuggestion(
                original_code=original_code,
                suggested_code=parsed.get('optimized_code', ''),
                explanation=parsed.get('explanation', ''),
                confidence_score=float(parsed.get('confidence_score', 0.5)),
                performance_impact=parsed.get('performance_impact', '')
            )
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            raise Exception(f"Failed to parse LLama response: {e}")