import ast
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import os

# Optional imports with fallbacks
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("Warning: networkx not available. Dependency analysis will be limited.")

try:
    import tree_sitter
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False
    print("Warning: tree-sitter not available. Using basic AST parsing only.")

@dataclass
class AnalysisResult:
    complexity_issues: List[str]
    performance_bottlenecks: List[str]
    hecs_patterns: List[str]
    code_smells: List[str]
    security_issues: List[str]
    inefficiencies: List[str]
    redundant_entities: List[str]
    bottlenecks: List[str]
    dependency_issues: List[str]
    performance_hotspots: List[str]

class HECSAnalyzer:
    def __init__(self):
        if HAS_NETWORKX:
            self.dependency_graph = nx.DiGraph()
        else:
            self.dependency_graph = None
        self.entity_components = {}
        self.system_dependencies = {}
    
    def analyze_code(self, code_or_path: str, language: str) -> AnalysisResult:
        """Main analysis entry point for HECS code
        
        Args:
            code_or_path: Either a file path or the actual code string
            language: Programming language (python, cpp, rust, etc.)
        """
        # Determine if input is a file path or code string
        if self._is_file_path(code_or_path):
            # It's a file path
            with open(code_or_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        else:
            # It's actual code
            code_content = code_or_path
        
        if language == 'python':
            return self._analyze_python_hecs(code_content)
        elif language == 'cpp':
            return self._analyze_cpp_hecs(code_content)
        elif language == 'rust':
            return self._analyze_rust_hecs(code_content)
        else:
            return self._analyze_generic_code(code_content, language)
    
    def _is_file_path(self, input_str: str) -> bool:
        """Determine if the input string is a file path or actual code"""
        # Check if it looks like a file path
        if len(input_str) < 500 and ('\\' in input_str or '/' in input_str) and not '\n' in input_str:
            return os.path.exists(input_str)
        return False
    
    def _analyze_python_hecs(self, code_content: str) -> AnalysisResult:
        """Analyze Python HECS implementation"""
        try:
            tree = ast.parse(code_content)
        except SyntaxError as e:
            return AnalysisResult(
                complexity_issues=[f"Syntax error: {e}"],
                performance_bottlenecks=[],
                hecs_patterns=[],
                code_smells=[],
                security_issues=[],
                inefficiencies=[],
                redundant_entities=[],
                bottlenecks=[],
                dependency_issues=[],
                performance_hotspots=[]
            )
        
        complexity_issues = []
        performance_bottlenecks = []
        hecs_patterns = []
        code_smells = []
        security_issues = []
        
        # Analyze AST for various issues
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for nested loops
                for child in ast.walk(node):
                    if isinstance(child, ast.For) and child != node:
                        complexity_issues.append("Nested loops detected - consider optimization")
                        performance_bottlenecks.append("O(n²) complexity from nested loops")
                        break
            
            elif isinstance(node, ast.FunctionDef):
                # Check for long functions
                if len(node.body) > 20:
                    code_smells.append(f"Function '{node.name}' is too long ({len(node.body)} statements)")
                
                # Check for inefficient patterns
                func_code = ast.unparse(node) if hasattr(ast, 'unparse') else str(node.name)
                if 'range(len(' in func_code:
                    code_smells.append(f"Function '{node.name}' uses range(len()) - consider enumerate()")
        
        # Check for list comprehension opportunities
        lines = code_content.split('\n')
        for i, line in enumerate(lines):
            if 'for ' in line and 'append(' in line:
                code_smells.append(f"Line {i+1}: Consider using list comprehension instead of append in loop")
        
        return AnalysisResult(
            complexity_issues=complexity_issues,
            performance_bottlenecks=performance_bottlenecks,
            hecs_patterns=hecs_patterns,
            code_smells=code_smells,
            security_issues=security_issues,
            inefficiencies=complexity_issues + performance_bottlenecks,
            redundant_entities=[],
            bottlenecks=performance_bottlenecks,
            dependency_issues=[],
            performance_hotspots=performance_bottlenecks
        )
    
    def _analyze_cpp_hecs(self, code_content: str) -> AnalysisResult:
        """Analyze C++ HECS implementation"""
        return self._analyze_generic_code(code_content, 'cpp')
    
    def _analyze_rust_hecs(self, code_content: str) -> AnalysisResult:
        """Analyze Rust HECS implementation"""
        return self._analyze_generic_code(code_content, 'rust')
    
    def _analyze_generic_code(self, code_content: str, language: str) -> AnalysisResult:
        """Generic code analysis for unsupported languages"""
        issues = []
        performance_issues = []
        
        # Basic pattern matching for common issues
        lines = code_content.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check for nested loops
            if 'for' in line_lower and any('for' in lines[j].lower() for j in range(i+1, min(i+10, len(lines)))):
                issues.append(f"Line {i+1}: Potential nested loop detected")
                performance_issues.append(f"Line {i+1}: Nested loop may cause performance issues")
            
            # Check for inefficient patterns
            if any(pattern in line_lower for pattern in ['sleep', 'wait', 'delay']):
                performance_issues.append(f"Line {i+1}: Blocking operation detected")
        
        return AnalysisResult(
            complexity_issues=issues,
            performance_bottlenecks=performance_issues,
            hecs_patterns=[],
            code_smells=[],
            security_issues=[],
            inefficiencies=issues,
            redundant_entities=[],
            bottlenecks=performance_issues,
            dependency_issues=[],
            performance_hotspots=performance_issues
        )