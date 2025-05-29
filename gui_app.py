from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import os
from src.core.analyzer import HECSAnalyzer
from src.core.refactor import HECSRefactorer
from src.core.ollama_integration import OllamaIntegration

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hecs_refactoring_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
analyzer = HECSAnalyzer()
refactorer = HECSRefactorer()
# Use OllamaIntegration instead of LlamaRefactoringEngine
ollama_engine = OllamaIntegration()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('analyze_code')
def handle_code_analysis(data):
    try:
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code.strip():
            emit('analysis_result', {'error': 'No code provided'})
            return
        
        # Analyze the code
        analysis_result = analyzer.analyze_code(code, language)
        
        # Get AI suggestions using OllamaIntegration
        ai_suggestions = []
        try:
            context = {
                'issues': analysis_result.complexity_issues + analysis_result.performance_bottlenecks + analysis_result.code_smells,
                'complexity_score': len(analysis_result.complexity_issues),
                'performance_issues': analysis_result.performance_bottlenecks
            }
            suggestion_result = ollama_engine.get_suggestions(code, context)
            if suggestion_result['status'] == 'success':
                ai_suggestions = [suggestion_result['suggestions']]
            else:
                print(f"AI suggestion failed: {suggestion_result['suggestions']}")
        except Exception as e:
            print(f"AI suggestion failed: {e}")
        
        # Calculate metrics
        total_issues = len(analysis_result.complexity_issues) + len(analysis_result.performance_bottlenecks) + len(analysis_result.code_smells) + len(analysis_result.security_issues)
        complexity_score = len(analysis_result.complexity_issues)
        performance_score = max(0, 100 - (len(analysis_result.performance_bottlenecks) * 10))
        quality_score = max(0, 100 - (total_issues * 5))
        
        # Format response to match frontend expectations
        response = {
            'analysis': {
                'complexity_issues': analysis_result.complexity_issues,
                'performance_bottlenecks': analysis_result.performance_bottlenecks,
                'hecs_patterns': analysis_result.hecs_patterns,
                'code_smells': analysis_result.code_smells,
                'security_issues': analysis_result.security_issues
            },
            'inefficiencies': analysis_result.inefficiencies,
            'bottlenecks': analysis_result.bottlenecks,
            'performance_hotspots': analysis_result.performance_hotspots,
            'ai_suggestions': ai_suggestions,
            'metrics': {
                'total_issues': total_issues,
                'complexity_score': complexity_score,
                'performance_score': performance_score,
                'quality_score': quality_score,
                'lines_of_code': len(code.split('\n')),
                'cyclomatic_complexity': complexity_score
            },
            'recommendations': {
                'refactoring_needed': total_issues > 3,
                'priority_areas': [],
                'estimated_improvement': min(50, total_issues * 10) if total_issues > 0 else 0
            }
        }
        
        # Add priority recommendations
        if analysis_result.performance_bottlenecks:
            response['recommendations']['priority_areas'].append('Performance Optimization')
        if analysis_result.complexity_issues:
            response['recommendations']['priority_areas'].append('Code Complexity Reduction')
        if analysis_result.code_smells:
            response['recommendations']['priority_areas'].append('Code Quality Improvement')
        if analysis_result.security_issues:
            response['recommendations']['priority_areas'].append('Security Fixes')
            
        if not response['recommendations']['priority_areas']:
            response['recommendations']['priority_areas'] = ['Code is well-structured']
        
        emit('analysis_result', response)
        
    except Exception as e:
        emit('analysis_result', {'error': f'Analysis failed: {str(e)}'})

@socketio.on('refactor_code')
def handle_code_refactoring(data):
    try:
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code.strip():
            emit('refactor_result', {'error': 'No code provided'})
            return
        
        # First analyze the code
        analysis_result = analyzer.analyze_code(code, language)
        
        # Then refactor it - pass code string instead of file path
        refactored_code = refactorer.refactor_code_string(code, analysis_result, language)
        
        # Get AI suggestions for the refactored code
        ai_suggestions = []
        try:
            context = {
                'language': language,
                'refactoring_applied': True,
                'original_issues': len(getattr(analysis_result, 'issues', []))
            }
            suggestion_result = ollama_engine.get_suggestions(refactored_code, context)
            if suggestion_result['status'] == 'success':
                ai_suggestions = [suggestion_result['suggestions']]
        except Exception as e:
            print(f"AI suggestion failed: {e}")
        
        response = {
            'refactored_code': refactored_code,
            'ai_suggestions': ai_suggestions,
            'improvements': {
                'complexity_reduced': len(getattr(analysis_result, 'complexity_issues', [])),
                'performance_improved': len(getattr(analysis_result, 'performance_bottlenecks', [])),
                'code_smells_fixed': len(getattr(analysis_result, 'code_smells', []))
            }
        }
        
        emit('refactor_result', response)
        
    except Exception as e:
        emit('refactor_result', {'error': f'Refactoring failed: {str(e)}'})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'HECS Refactoring GUI'})

if __name__ == '__main__':
    print("Starting HECS Refactoring GUI...")
    print("Open your browser and go to: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)