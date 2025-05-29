import time
import psutil
import subprocess
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    execution_time: float
    memory_usage: float
    cpu_usage: float
    custom_metrics: Dict[str, float]

class HECSBenchmarker:
    def __init__(self):
        self.baseline_results = {}
        self.refactored_results = {}
    
    def benchmark_code(self, code_path: str, test_cases: List[str]) -> BenchmarkResult:
        """Benchmark HECS code performance"""
        execution_times = []
        memory_usages = []
        cpu_usages = []
        
        for test_case in test_cases:
            result = self._run_single_benchmark(code_path, test_case)
            execution_times.append(result.execution_time)
            memory_usages.append(result.memory_usage)
            cpu_usages.append(result.cpu_usage)
        
        return BenchmarkResult(
            execution_time=sum(execution_times) / len(execution_times),
            memory_usage=sum(memory_usages) / len(memory_usages),
            cpu_usage=sum(cpu_usages) / len(cpu_usages),
            custom_metrics=self._calculate_custom_metrics(code_path)
        )
    
    def _run_single_benchmark(self, code_path: str, test_case: str) -> BenchmarkResult:
        """Run a single benchmark test"""
        process = psutil.Process()
        
        # Measure baseline metrics
        start_memory = process.memory_info().rss
        start_cpu = process.cpu_percent()
        start_time = time.time()
        
        # Execute test case
        try:
            result = subprocess.run(
                ['python', code_path, test_case],
                capture_output=True,
                text=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            raise Exception(f"Benchmark timeout for test case: {test_case}")
        
        # Measure final metrics
        end_time = time.time()
        end_memory = process.memory_info().rss
        end_cpu = process.cpu_percent()
        
        return BenchmarkResult(
            execution_time=end_time - start_time,
            memory_usage=end_memory - start_memory,
            cpu_usage=end_cpu - start_cpu,
            custom_metrics={}
        )
    
    def compare_performance(self, baseline: BenchmarkResult, refactored: BenchmarkResult) -> Dict:
        """Compare performance between baseline and refactored code"""
        return {
            'execution_time_improvement': (
                (baseline.execution_time - refactored.execution_time) / baseline.execution_time * 100
            ),
            'memory_usage_improvement': (
                (baseline.memory_usage - refactored.memory_usage) / baseline.memory_usage * 100
            ),
            'cpu_usage_improvement': (
                (baseline.cpu_usage - refactored.cpu_usage) / baseline.cpu_usage * 100
            ),
            'overall_score': self._calculate_overall_score(baseline, refactored)
        }
    
    def _calculate_custom_metrics(self, code_path: str) -> Dict[str, float]:
        """Calculate HECS-specific performance metrics"""
        return {
            'entity_creation_rate': 0.0,
            'component_access_time': 0.0,
            'system_update_frequency': 0.0
        }
    
    def _calculate_overall_score(self, baseline: BenchmarkResult, refactored: BenchmarkResult) -> float:
        """Calculate overall performance improvement score"""
        # Weighted scoring based on different metrics
        time_weight = 0.4
        memory_weight = 0.3
        cpu_weight = 0.3
        
        time_improvement = (baseline.execution_time - refactored.execution_time) / baseline.execution_time
        memory_improvement = (baseline.memory_usage - refactored.memory_usage) / baseline.memory_usage
        cpu_improvement = (baseline.cpu_usage - refactored.cpu_usage) / baseline.cpu_usage
        
        return (time_improvement * time_weight + 
                memory_improvement * memory_weight + 
                cpu_improvement * cpu_weight) * 100