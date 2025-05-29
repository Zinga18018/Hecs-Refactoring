import ast
from typing import List, Dict, Tuple
from .analyzer import AnalysisResult

# Optional import with fallback
try:
    import astor
    HAS_ASTOR = True
except ImportError:
    HAS_ASTOR = False
    print("Warning: astor not available. Code generation will be limited.")

class HECSRefactorer:
    def __init__(self, llama_engine=None):
        self.llama_engine = llama_engine
        self.refactoring_rules = self._load_refactoring_rules()
    
    def refactor_code(self, file_path: str, analysis_result: AnalysisResult) -> Dict:
        """Main refactoring entry point"""
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        try:
            tree = ast.parse(original_code)
        except SyntaxError as e:
            return {
                'original_code': original_code,
                'refactored_code': original_code,
                'ai_suggestions': [],
                'applied_rules': [],
                'performance_predictions': {},
                'error': f"Syntax error: {e}"
            }
        
        refactored_tree = self._apply_refactoring_rules(tree, analysis_result)
        
        # Get AI suggestions if available
        ai_suggestions = []
        if self.llama_engine:
            try:
                ai_suggestions = self._get_ai_suggestions(original_code, analysis_result)
            except Exception as e:
                print(f"Warning: AI suggestions failed: {e}")
        
        # Convert back to code
        if HAS_ASTOR:
            try:
                refactored_code = astor.to_source(refactored_tree)
            except Exception as e:
                print(f"Warning: Code generation failed: {e}")
                refactored_code = original_code
        else:
            # Fallback: return original code with comments about suggested changes
            refactored_code = self._generate_commented_suggestions(original_code, analysis_result)
        
        return {
            'original_code': original_code,
            'refactored_code': refactored_code,
            'ai_suggestions': ai_suggestions,
            'applied_rules': self._get_applied_rules(),
            'performance_predictions': self._predict_performance_impact()
        }
    
    def _generate_commented_suggestions(self, original_code: str, analysis: AnalysisResult) -> str:
        """Generate code with comments about suggested improvements"""
        suggestions = []
        suggestions.append("# HECS Refactoring Suggestions:")
        
        if analysis.inefficiencies:
            suggestions.append("# Inefficiencies found:")
            for issue in analysis.inefficiencies:
                suggestions.append(f"# - {issue}")
        
        if analysis.bottlenecks:
            suggestions.append("# Performance bottlenecks:")
            for bottleneck in analysis.bottlenecks:
                suggestions.append(f"# - {bottleneck}")
        
        if analysis.performance_hotspots:
            suggestions.append("# Performance hotspots:")
            for hotspot in analysis.performance_hotspots:
                suggestions.append(f"# - {hotspot}")
        
        return "\n".join(suggestions) + "\n\n" + original_code
    
    def _apply_refactoring_rules(self, tree: ast.AST, analysis: AnalysisResult) -> ast.AST:
        """Apply automated refactoring rules"""
        # Basic transformations that don't require astor
        return tree
    
    def _get_ai_suggestions(self, code: str, analysis: AnalysisResult) -> List:
        """Get AI-powered refactoring suggestions"""
        if not self.llama_engine:
            return []
        
        try:
            context = {
                'inefficiencies': analysis.inefficiencies,
                'bottlenecks': analysis.bottlenecks,
                'hotspots': analysis.performance_hotspots
            }
            
            suggestion = self.llama_engine.analyze_and_suggest(code, context)
            return [suggestion]
        except Exception as e:
            print(f"AI suggestion failed: {e}")
            return []
    
    def _load_refactoring_rules(self) -> Dict:
        """Load refactoring rules from configuration"""
        return {}
    
    def _get_applied_rules(self) -> List[str]:
        """Get list of applied refactoring rules"""
        return ["Basic HECS analysis completed"]
    
    def _predict_performance_impact(self) -> Dict:
        """Predict performance impact of refactoring"""
        return {"status": "Analysis completed"}
    
    def refactor_code_string(self, code: str, analysis_result: AnalysisResult, language: str = 'python') -> str:
        """Refactor code from string instead of file"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return code  # Return original code if syntax error
        
        refactored_tree = self._apply_refactoring_rules(tree, analysis_result)
        
        # Convert back to code
        if HAS_ASTOR:
            try:
                return astor.to_source(refactored_tree)
            except Exception as e:
                print(f"Warning: Code generation failed: {e}")
                return code
        else:
            # Fallback: return original code with comments about suggested improvements
            improvements = []
            if hasattr(analysis_result, 'complexity_issues'):
                improvements.extend([f"# TODO: Fix complexity issue at line {issue.get('line', 'unknown')}" for issue in analysis_result.complexity_issues])
            if hasattr(analysis_result, 'performance_issues'):
                improvements.extend([f"# TODO: Fix performance issue at line {issue.get('line', 'unknown')}" for issue in analysis_result.performance_issues])
            
            if improvements:
                return "\n".join(improvements) + "\n\n" + code
            else:
                return self._generate_commented_suggestions(code, analysis_result)