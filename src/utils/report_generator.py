import json
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    """Generates HTML and JSON reports for HECS refactoring results."""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / 'templates'
    
    def generate_html_report(self, report_data):
        """Generate an HTML report from refactoring data."""
        html_template = self._get_html_template()
        
        # Format the data for HTML display
        analysis_summary = self._format_analysis_summary(report_data.get('analysis', {}))
        refactoring_summary = self._format_refactoring_summary(report_data.get('refactoring', {}))
        benchmark_summary = self._format_benchmark_summary(report_data.get('benchmark'))
        
        # Replace placeholders in template
        html_content = html_template.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            input_file=report_data.get('input_file', 'Unknown'),
            language=report_data.get('language', 'Unknown'),
            analysis_summary=analysis_summary,
            refactoring_summary=refactoring_summary,
            benchmark_summary=benchmark_summary
        )
        
        return html_content
    
    def _format_analysis_summary(self, analysis_data):
        """Format analysis data for HTML display."""
        if not analysis_data:
            return "<p>No analysis data available.</p>"
        
        # Handle AnalysisResult dataclass
        if hasattr(analysis_data, 'inefficiencies'):
            # Convert dataclass to dict-like structure
            analysis_dict = {
                'inefficiencies': analysis_data.inefficiencies,
                'redundant_entities': analysis_data.redundant_entities,
                'bottlenecks': analysis_data.bottlenecks,
                'dependency_issues': analysis_data.dependency_issues,
                'performance_hotspots': analysis_data.performance_hotspots
            }
            analysis_data = analysis_dict
        
        html = "<div class='analysis-section'>\n"
        
        # Inefficiencies
        if 'inefficiencies' in analysis_data and analysis_data['inefficiencies']:
            html += "<h3>Code Inefficiencies</h3>\n<ul>\n"
            for issue in analysis_data['inefficiencies']:
                html += f"<li>{issue}</li>\n"
            html += "</ul>\n"
        
        # Performance bottlenecks
        if 'bottlenecks' in analysis_data and analysis_data['bottlenecks']:
            html += "<h3>Performance Bottlenecks</h3>\n<ul>\n"
            for bottleneck in analysis_data['bottlenecks']:
                html += f"<li>{bottleneck}</li>\n"
            html += "</ul>\n"
        
        # Performance hotspots
        if 'performance_hotspots' in analysis_data and analysis_data['performance_hotspots']:
            html += "<h3>Performance Hotspots</h3>\n<ul>\n"
            for hotspot in analysis_data['performance_hotspots']:
                html += f"<li>{hotspot}</li>\n"
            html += "</ul>\n"
        
        # Redundant entities
        if 'redundant_entities' in analysis_data and analysis_data['redundant_entities']:
            html += "<h3>Redundant Entities</h3>\n<ul>\n"
            for entity in analysis_data['redundant_entities']:
                html += f"<li>{entity}</li>\n"
            html += "</ul>\n"
        
        # Dependency issues
        if 'dependency_issues' in analysis_data and analysis_data['dependency_issues']:
            html += "<h3>Dependency Issues</h3>\n<ul>\n"
            for issue in analysis_data['dependency_issues']:
                html += f"<li>{issue}</li>\n"
            html += "</ul>\n"
        
        # If no issues found
        if not any(analysis_data.get(key) for key in ['inefficiencies', 'bottlenecks', 'performance_hotspots', 'redundant_entities', 'dependency_issues']):
            html += "<p>No significant issues detected in the code analysis.</p>\n"
        
        html += "</div>\n"
        return html
    
    def _format_refactoring_summary(self, refactoring_data):
        """Format refactoring data for HTML display."""
        if not refactoring_data:
            return "<p>No refactoring data available.</p>"
        
        html = "<div class='refactoring-section'>\n"
        
        # Applied rules
        if 'applied_rules' in refactoring_data and refactoring_data['applied_rules']:
            rules = refactoring_data['applied_rules']
            html += "<h3>Applied Refactoring Rules</h3>\n<ul>\n"
            for rule in rules:
                html += f"<li>{rule}</li>\n"
            html += "</ul>\n"
        
        # AI suggestions
        if 'ai_suggestions' in refactoring_data and refactoring_data['ai_suggestions']:
            suggestions = refactoring_data['ai_suggestions']
            html += "<h3>AI-Generated Suggestions</h3>\n<ul>\n"
            for suggestion in suggestions:
                html += f"<li>{suggestion}</li>\n"
            html += "</ul>\n"
        
        # Code changes summary
        if 'changes_summary' in refactoring_data:
            summary = refactoring_data['changes_summary']
            html += "<h3>Changes Summary</h3>\n"
            html += f"<p><strong>Lines Added:</strong> {summary.get('lines_added', 0)}</p>\n"
            html += f"<p><strong>Lines Removed:</strong> {summary.get('lines_removed', 0)}</p>\n"
            html += f"<p><strong>Lines Modified:</strong> {summary.get('lines_modified', 0)}</p>\n"
        
        # Refactored code preview
        if 'refactored_code' in refactoring_data:
            html += "<h3>Refactoring Status</h3>\n"
            html += "<p>✅ Code has been successfully refactored</p>\n"
        
        html += "</div>\n"
        return html
    
    def _format_benchmark_summary(self, benchmark_data):
        """Format benchmark data for HTML display."""
        if not benchmark_data:
            return "<p>No benchmark data available. Run with --benchmark flag to enable performance comparison.</p>"
        
        html = "<div class='benchmark-section'>\n"
        html += "<h3>Performance Comparison</h3>\n"
        
        html += f"<p><strong>Execution Time Improvement:</strong> {benchmark_data.get('execution_time_improvement', 0):.2f}%</p>\n"
        html += f"<p><strong>Memory Usage Improvement:</strong> {benchmark_data.get('memory_usage_improvement', 0):.2f}%</p>\n"
        html += f"<p><strong>Overall Score:</strong> {benchmark_data.get('overall_score', 0):.2f}</p>\n"
        
        html += "</div>\n"
        return html
    
    def _get_html_template(self):
        """Get the HTML template for reports."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HECS Refactoring Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        .meta-info {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            border-left: 4px solid #3498db;
            background-color: #f8f9fa;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 5px;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 HECS Refactoring Report</h1>
        
        <div class="meta-info">
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Input File:</strong> {input_file}</p>
            <p><strong>Language:</strong> {language}</p>
        </div>
        
        <div class="section">
            <h2>📊 Code Analysis</h2>
            {analysis_summary}
        </div>
        
        <div class="section">
            <h2>🔧 Refactoring Results</h2>
            {refactoring_summary}
        </div>
        
        <div class="section">
            <h2>⚡ Performance Benchmarks</h2>
            {benchmark_summary}
        </div>
    </div>
</body>
</html>
        """