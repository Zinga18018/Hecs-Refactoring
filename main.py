import argparse
import json
import os
from pathlib import Path
from src.core.analyzer import HECSAnalyzer
from src.core.refactor import HECSRefactorer
from src.core.llama_integration import LlamaRefactoringEngine
from src.core.benchmarker import HECSBenchmarker
from src.utils.report_generator import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description='AI-Powered HECS Refactoring Tool')
    parser.add_argument('input_file', help='Path to HECS code file to analyze')
    parser.add_argument('--language', choices=['python', 'cpp', 'rust'], default='python',
                       help='Programming language of the input file')
    parser.add_argument('--llama-endpoint', default='http://localhost:11434/api/generate',
                       help='LLama model API endpoint')
    parser.add_argument('--api-key', help='API key for LLama model')
    parser.add_argument('--output-dir', default='./output', help='Output directory for results')
    parser.add_argument('--benchmark', action='store_true', help='Run performance benchmarks')
    parser.add_argument('--config', help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return 1
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Analyzing HECS code: {args.input_file}")
    
    # Initialize components
    analyzer = HECSAnalyzer()
    llama_engine = LlamaRefactoringEngine(args.llama_endpoint, args.api_key)
    refactorer = HECSRefactorer(llama_engine)
    benchmarker = HECSBenchmarker() if args.benchmark else None
    report_generator = ReportGenerator()
    
    try:
        # Step 1: Analyze code
        print("📊 Running code analysis...")
        analysis_result = analyzer.analyze_code(args.input_file, args.language)
        
        # Step 2: Refactor code
        print("🔧 Applying refactoring suggestions...")
        refactoring_result = refactorer.refactor_code(args.input_file, analysis_result)
        
        # Step 3: Benchmark (if requested)
        benchmark_comparison = None
        if args.benchmark:
            print("⚡ Running performance benchmarks...")
            # Save refactored code temporarily for benchmarking
            temp_refactored_file = output_dir / 'temp_refactored.py'
            with open(temp_refactored_file, 'w', encoding='utf-8') as f:
                f.write(refactoring_result['refactored_code'])
            
            baseline_result = benchmarker.benchmark_code(args.input_file, ['test_case_1'])
            refactored_result = benchmarker.benchmark_code(str(temp_refactored_file), ['test_case_1'])
            benchmark_comparison = benchmarker.compare_performance(baseline_result, refactored_result)
            
            # Clean up temporary file
            temp_refactored_file.unlink()
        
        # Step 4: Generate reports
        print("📋 Generating reports...")
        report_data = {
            'analysis': analysis_result,
            'refactoring': refactoring_result,
            'benchmark': benchmark_comparison,
            'input_file': args.input_file,
            'language': args.language
        }
        
        # Save refactored code
        refactored_file = output_dir / f'refactored_{Path(args.input_file).name}'
        with open(refactored_file, 'w', encoding='utf-8') as f:
            f.write(refactoring_result['refactored_code'])
        
        # Generate HTML report with UTF-8 encoding
        html_report = report_generator.generate_html_report(report_data)
        report_file = output_dir / 'refactoring_report.html'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # Generate JSON summary
        json_report = output_dir / 'refactoring_summary.json'
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"✅ Refactoring complete!")
        print(f"📁 Results saved to: {output_dir}")
        print(f"📄 Refactored code: {refactored_file}")
        print(f"📊 HTML report: {report_file}")
        print(f"📋 JSON summary: {json_report}")
        
        # Display summary
        if benchmark_comparison:
            print(f"\n⚡ Performance Improvements:")
            print(f"   Execution Time: {benchmark_comparison['execution_time_improvement']:.2f}%")
            print(f"   Memory Usage: {benchmark_comparison['memory_usage_improvement']:.2f}%")
            print(f"   Overall Score: {benchmark_comparison['overall_score']:.2f}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during refactoring: {e}")
        return 1

if __name__ == '__main__':
    exit(main())