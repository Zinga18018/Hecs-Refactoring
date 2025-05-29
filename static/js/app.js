class HECSRefactoringApp {
    constructor() {
        this.socket = io();
        this.editor = null;
        this.currentLanguage = 'python';
        this.isAnalyzing = false;
        this.isRefactoring = false;
        this.charts = {};
        this.stats = {
            totalAnalyses: 0,
            issuesFound: 0,
            improvementScore: 0
        };
        
        this.initializeEditor();
        this.setupEventListeners();
        this.setupSocketListeners();
        this.initializeCharts();
        this.updateStats();
    }

    initializeEditor() {
        const textarea = document.getElementById('codeEditor');
        this.editor = CodeMirror.fromTextArea(textarea, {
            lineNumbers: true,
            mode: 'python',
            theme: 'monokai',
            indentUnit: 4,
            lineWrapping: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            foldGutter: true,
            gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
            extraKeys: {
                'Ctrl-Space': 'autocomplete',
                'F11': function(cm) {
                    cm.setOption('fullScreen', !cm.getOption('fullScreen'));
                },
                'Esc': function(cm) {
                    if (cm.getOption('fullScreen')) cm.setOption('fullScreen', false);
                }
            }
        });

        // Set sample code
        this.editor.setValue(`# Sample HECS code with inefficiencies
import time
import threading
from typing import List, Dict

class DataProcessor:
    def __init__(self):
        self.data = []
        self.cache = {}
        
    def inefficient_search(self, target):
        # O(n²) search - performance issue
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                if self.data[i][j] == target:
                    return (i, j)
        return None
    
    def memory_leak_function(self):
        # Potential memory leak
        large_data = []
        for i in range(100000):
            large_data.append([x for x in range(1000)])
        return large_data
    
    def blocking_operation(self, items):
        # Synchronous operations that could be async
        results = []
        for item in items:
            time.sleep(0.1)  # Simulating I/O
            results.append(f"Processed {item}")
        return results`);

        // Update stats on code change
        this.editor.on('change', () => {
            this.updateCodeStats();
        });
        
        this.updateCodeStats();
    }

    updateCodeStats() {
        const code = this.editor.getValue();
        const lines = code.split('\n').length;
        const chars = code.length;
        const complexity = this.calculateComplexity(code);
        
        document.getElementById('lineCount').textContent = `Lines: ${lines}`;
        document.getElementById('charCount').textContent = `Characters: ${chars}`;
        document.getElementById('complexity').textContent = `Complexity: ${complexity}`;
    }

    calculateComplexity(code) {
        const complexityKeywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with'];
        let complexity = 0;
        
        complexityKeywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'g');
            const matches = code.match(regex);
            if (matches) complexity += matches.length;
        });
        
        if (complexity < 5) return 'Low';
        if (complexity < 15) return 'Medium';
        return 'High';
    }

    setupEventListeners() {
        // Language selection
        document.getElementById('languageSelect').addEventListener('change', (e) => {
            this.currentLanguage = e.target.value;
            const modeMap = {
                'python': 'python',
                'javascript': 'javascript',
                'java': 'text/x-java',
                'cpp': 'text/x-c++src'
            };
            this.editor.setOption('mode', modeMap[this.currentLanguage]);
        });

        // Analyze button
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzeCode();
        });

        // Refactor button
        document.getElementById('refactorBtn').addEventListener('click', () => {
            this.refactorCode();
        });

        // Clear button
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.editor.setValue('');
            this.clearResults();
        });

        // Copy refactored code button
        document.getElementById('copyRefactoredBtn').addEventListener('click', () => {
            this.copyRefactoredCode();
        });

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
        });

        this.socket.on('analysis_result', (data) => {
            this.handleAnalysisResult(data);
        });

        this.socket.on('refactoring_result', (data) => {
            this.handleRefactoringResult(data);
        });

        this.socket.on('error', (error) => {
            this.showError(error.message);
        });
    }

    initializeCharts() {
        // Complexity Chart
        const complexityCtx = document.getElementById('complexityChart').getContext('2d');
        this.charts.complexity = new Chart(complexityCtx, {
            type: 'doughnut',
            data: {
                labels: ['Low', 'Medium', 'High'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Issue Distribution Chart
        const issueCtx = document.getElementById('issueChart').getContext('2d');
        this.charts.issues = new Chart(issueCtx, {
            type: 'bar',
            data: {
                labels: ['Performance', 'Memory', 'Logic', 'Style'],
                datasets: [{
                    label: 'Issues Found',
                    data: [0, 0, 0, 0],
                    backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#6f42c1'],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // Trend Chart
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        this.charts.trend = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Code Quality Score',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    analyzeCode() {
        if (this.isAnalyzing) return;
        
        const code = this.editor.getValue().trim();
        if (!code) {
            this.showError('Please enter some code to analyze');
            return;
        }

        this.isAnalyzing = true;
        this.showLoading('Analyzing code...');
        this.updateStatus('Analyzing code...', true);
        
        this.socket.emit('analyze_code', {
            code: code,
            language: this.currentLanguage
        });
    }

    refactorCode() {
        if (this.isRefactoring) return;
        
        const code = this.editor.getValue().trim();
        if (!code) {
            this.showError('Please enter some code to refactor');
            return;
        }

        this.isRefactoring = true;
        this.showLoading('Refactoring code...');
        this.updateStatus('Refactoring code...', true);
        
        this.socket.emit('refactor_code', {
            code: code,
            language: this.currentLanguage
        });
    }

    handleAnalysisResult(data) {
        this.isAnalyzing = false;
        this.hideLoading();
        this.updateStatus('Analysis complete', false);
        
        if (data.error) {
            this.showError(data.error);
            return;
        }

        // Update statistics
        this.stats.totalAnalyses++;
        this.stats.issuesFound = data.metrics?.total_issues || 0;
        this.updateStats();

        // Display comprehensive analysis results
        this.displayComprehensiveAnalysis(data);
        this.displayAISuggestions(data.ai_suggestions || []);
        this.displayMetrics(data.metrics || {});
        this.displayRecommendations(data.recommendations || {});
        this.updateCharts(data);
        
        // Switch to analysis tab
        this.switchTab('analysis');
        
        // Add fade-in animation
        document.querySelector('#analysis-panel').classList.add('fade-in');
    }

    displayComprehensiveAnalysis(data) {
        // Display complexity issues
        const complexityList = document.getElementById('issuesList');
        if (data.analysis?.complexity_issues && data.analysis.complexity_issues.length > 0) {
            complexityList.innerHTML = data.analysis.complexity_issues.map((issue, index) => `
                <div class="issue-item error">
                    <div class="issue-header">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div class="issue-title">Complexity Issue #${index + 1}</div>
                        <span class="issue-severity high">High</span>
                    </div>
                    <div class="issue-description">${issue}</div>
                    <div class="issue-impact">Impact: Increased maintenance difficulty</div>
                </div>
            `).join('');
        } else {
            complexityList.innerHTML = `
                <div class="success-message">
                    <i class="fas fa-check-circle"></i>
                    <span>No complexity issues detected - Code structure is well-organized</span>
                </div>
            `;
        }

        // Display performance bottlenecks
        const performanceList = document.getElementById('hotspotsList');
        if (data.analysis?.performance_bottlenecks && data.analysis.performance_bottlenecks.length > 0) {
            performanceList.innerHTML = data.analysis.performance_bottlenecks.map((bottleneck, index) => `
                <div class="issue-item warning">
                    <div class="issue-header">
                        <i class="fas fa-tachometer-alt"></i>
                        <div class="issue-title">Performance Bottleneck #${index + 1}</div>
                        <span class="issue-severity medium">Medium</span>
                    </div>
                    <div class="issue-description">${bottleneck}</div>
                    <div class="issue-impact">Impact: Reduced execution speed</div>
                </div>
            `).join('');
        } else {
            performanceList.innerHTML = `
                <div class="success-message">
                    <i class="fas fa-check-circle"></i>
                    <span>No performance bottlenecks detected - Code runs efficiently</span>
                </div>
            `;
        }

        // Display code smells
        const smellsList = document.getElementById('smellsList');
        if (data.analysis?.code_smells && data.analysis.code_smells.length > 0) {
            smellsList.innerHTML = data.analysis.code_smells.map((smell, index) => `
                <div class="issue-item info">
                    <div class="issue-header">
                        <i class="fas fa-code"></i>
                        <div class="issue-title">Code Smell #${index + 1}</div>
                        <span class="issue-severity low">Low</span>
                    </div>
                    <div class="issue-description">${smell}</div>
                    <div class="issue-impact">Impact: Code readability and maintainability</div>
                </div>
            `).join('');
        } else {
            smellsList.innerHTML = `
                <div class="success-message">
                    <i class="fas fa-check-circle"></i>
                    <span>No code smells detected - Code follows best practices</span>
                </div>
            `;
        }

        // Display security issues if any
        if (data.analysis?.security_issues && data.analysis.security_issues.length > 0) {
            const securityHtml = data.analysis.security_issues.map((issue, index) => `
                <div class="issue-item critical">
                    <div class="issue-header">
                        <i class="fas fa-shield-alt"></i>
                        <div class="issue-title">Security Issue #${index + 1}</div>
                        <span class="issue-severity critical">Critical</span>
                    </div>
                    <div class="issue-description">${issue}</div>
                    <div class="issue-impact">Impact: Security vulnerability</div>
                </div>
            `).join('');
            
            // Add security section if it doesn't exist
            let securitySection = document.getElementById('securityList');
            if (!securitySection) {
                const analysisPanel = document.getElementById('analysis-panel');
                const securityDiv = document.createElement('div');
                securityDiv.innerHTML = `
                    <h3><i class="fas fa-shield-alt"></i> Security Issues</h3>
                    <div id="securityList"></div>
                `;
                analysisPanel.appendChild(securityDiv);
                securitySection = document.getElementById('securityList');
            }
            securitySection.innerHTML = securityHtml;
        }
    }

    displayMetrics(metrics) {
        // Update metrics display
        const metricsContainer = document.getElementById('metricsContainer') || this.createMetricsContainer();
        
        metricsContainer.innerHTML = `
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">${metrics.total_issues || 0}</div>
                    <div class="metric-label">Total Issues</div>
                    <div class="metric-trend ${metrics.total_issues > 5 ? 'negative' : 'positive'}">
                        <i class="fas fa-${metrics.total_issues > 5 ? 'arrow-down' : 'arrow-up'}"></i>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${metrics.quality_score || 0}%</div>
                    <div class="metric-label">Quality Score</div>
                    <div class="metric-trend ${metrics.quality_score < 70 ? 'negative' : 'positive'}">
                        <i class="fas fa-${metrics.quality_score < 70 ? 'arrow-down' : 'arrow-up'}"></i>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${metrics.performance_score || 0}%</div>
                    <div class="metric-label">Performance Score</div>
                    <div class="metric-trend ${metrics.performance_score < 70 ? 'negative' : 'positive'}">
                        <i class="fas fa-${metrics.performance_score < 70 ? 'arrow-down' : 'arrow-up'}"></i>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${metrics.lines_of_code || 0}</div>
                    <div class="metric-label">Lines of Code</div>
                    <div class="metric-trend neutral">
                        <i class="fas fa-code"></i>
                    </div>
                </div>
            </div>
        `;
    }

    displayRecommendations(recommendations) {
        const recommendationsContainer = document.getElementById('recommendationsContainer') || this.createRecommendationsContainer();
        
        const refactoringNeeded = recommendations.refactoring_needed;
        const priorityAreas = recommendations.priority_areas || [];
        const estimatedImprovement = recommendations.estimated_improvement || 0;
        
        recommendationsContainer.innerHTML = `
            <div class="recommendations-section">
                <h3><i class="fas fa-lightbulb"></i> Analysis Summary</h3>
                <div class="recommendation-status ${refactoringNeeded ? 'needs-attention' : 'good'}">
                    <i class="fas fa-${refactoringNeeded ? 'exclamation-triangle' : 'check-circle'}"></i>
                    <span>${refactoringNeeded ? 'Refactoring Recommended' : 'Code Quality is Good'}</span>
                </div>
                
                <div class="priority-areas">
                    <h4>Priority Areas:</h4>
                    <ul>
                        ${priorityAreas.map(area => `<li><i class="fas fa-arrow-right"></i> ${area}</li>`).join('')}
                    </ul>
                </div>
                
                ${estimatedImprovement > 0 ? `
                    <div class="improvement-estimate">
                        <h4>Estimated Improvement:</h4>
                        <div class="improvement-bar">
                            <div class="improvement-fill" style="width: ${Math.min(estimatedImprovement, 100)}%"></div>
                            <span class="improvement-text">${estimatedImprovement}% potential improvement</span>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    createMetricsContainer() {
        const analysisPanel = document.getElementById('analysis-panel');
        const container = document.createElement('div');
        container.id = 'metricsContainer';
        container.className = 'metrics-container';
        analysisPanel.insertBefore(container, analysisPanel.firstChild);
        return container;
    }

    createRecommendationsContainer() {
        const analysisPanel = document.getElementById('analysis-panel');
        const container = document.createElement('div');
        container.id = 'recommendationsContainer';
        container.className = 'recommendations-container';
        analysisPanel.appendChild(container);
        return container;
    }

    handleRefactoringResult(data) {
        this.isRefactoring = false;
        this.hideLoading();
        this.updateStatus('Refactoring complete', false);
        
        if (data.error) {
            this.showError(data.error);
            return;
        }

        // Display refactored code
        this.displayRefactoredCode(data.refactored_code);
        
        // Calculate improvement score
        const originalIssues = this.stats.issuesFound;
        const newIssues = data.remaining_issues || 0;
        const improvement = originalIssues > 0 ? Math.round(((originalIssues - newIssues) / originalIssues) * 100) : 0;
        this.stats.improvementScore = improvement;
        this.updateStats();
        
        // Switch to refactored tab
        this.switchTab('refactored');
    }

    displayAnalysisResults(data) {
        // Display issues
        const issuesList = document.getElementById('issuesList');
        if (data.inefficiencies && data.inefficiencies.length > 0) {
            issuesList.innerHTML = data.inefficiencies.map(issue => `
                <div class="issue-item">
                    <div class="issue-title">Performance Issue</div>
                    <div class="issue-description">${issue}</div>
                    <span class="issue-location">Line: Unknown</span>
                </div>
            `).join('');
        } else {
            issuesList.innerHTML = '<p class="placeholder">No performance issues detected</p>';
        }

        // Display hotspots
        const hotspotsList = document.getElementById('hotspotsList');
        if (data.performance_hotspots && data.performance_hotspots.length > 0) {
            hotspotsList.innerHTML = data.performance_hotspots.map(hotspot => `
                <div class="issue-item warning">
                    <div class="issue-title">Performance Hotspot</div>
                    <div class="issue-description">${hotspot}</div>
                    <span class="issue-location">Requires attention</span>
                </div>
            `).join('');
        } else {
            hotspotsList.innerHTML = '<p class="placeholder">No performance hotspots detected</p>';
        }

        // Display bottlenecks
        const smellsList = document.getElementById('smellsList');
        if (data.bottlenecks && data.bottlenecks.length > 0) {
            smellsList.innerHTML = data.bottlenecks.map(bottleneck => `
                <div class="issue-item info">
                    <div class="issue-title">Bottleneck</div>
                    <div class="issue-description">${bottleneck}</div>
                    <span class="issue-location">Optimization needed</span>
                </div>
            `).join('');
        } else {
            smellsList.innerHTML = '<p class="placeholder">No bottlenecks detected</p>';
        }
    }

    displayAISuggestions(suggestions) {
        const container = document.getElementById('aiSuggestions');
        
        if (suggestions && suggestions.length > 0) {
            // Parse suggestions into structured format
            const structuredSuggestions = this.parseStructuredSuggestions(suggestions);
            
            container.innerHTML = structuredSuggestions.map((suggestion, index) => `
                <div class="suggestion-card">
                    <div class="suggestion-header">
                        <div class="suggestion-priority ${suggestion.priority}">
                            <i class="fas ${this.getPriorityIcon(suggestion.priority)}"></i>
                            <span class="priority-label">${suggestion.priority.toUpperCase()}</span>
                        </div>
                        <div class="suggestion-category">${suggestion.category}</div>
                    </div>
                    
                    <div class="suggestion-content">
                        <h4 class="suggestion-title">${suggestion.title}</h4>
                        <p class="suggestion-description">${suggestion.description}</p>
                        
                        <div class="issue-details">
                            <div class="issue-location">
                                <i class="fas fa-map-marker-alt"></i>
                                <span>Line ${suggestion.line || 'Multiple'} - ${suggestion.function || 'Global scope'}</span>
                            </div>
                            <div class="issue-impact">
                                <i class="fas fa-exclamation-triangle"></i>
                                <span>Impact: ${suggestion.impact}</span>
                            </div>
                        </div>
                        
                        <div class="fix-section">
                            <h5><i class="fas fa-tools"></i> How to Fix:</h5>
                            <div class="fix-steps">
                                ${suggestion.fixes.map((fix, fixIndex) => `
                                    <div class="fix-step">
                                        <div class="step-number">${fixIndex + 1}</div>
                                        <div class="step-content">
                                            <p class="step-description">${fix.description}</p>
                                            ${fix.code ? `
                                                <div class="code-example">
                                                    <div class="code-header">
                                                        <span class="code-label">${fix.type === 'before' ? 'Before (Current)' : 'After (Fixed)'}</span>
                                                        <button class="copy-code-btn" onclick="this.copyCodeExample(this)">
                                                            <i class="fas fa-copy"></i>
                                                        </button>
                                                    </div>
                                                    <pre><code class="language-python">${this.escapeHtml(fix.code)}</code></pre>
                                                </div>
                                            ` : ''}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        
                        <div class="suggestion-benefits">
                            <h5><i class="fas fa-chart-line"></i> Expected Benefits:</h5>
                            <ul class="benefits-list">
                                ${suggestion.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                            </ul>
                        </div>
                        
                        <div class="suggestion-actions">
                            <button class="btn btn-primary apply-fix-btn" onclick="this.applyFix(${index})">
                                <i class="fas fa-magic"></i> Apply Fix
                            </button>
                            <button class="btn btn-outline learn-more-btn" onclick="this.showMoreInfo(${index})">
                                <i class="fas fa-info-circle"></i> Learn More
                            </button>
                            <button class="btn btn-outline dismiss-btn" onclick="this.dismissSuggestion(${index})">
                                <i class="fas fa-times"></i> Dismiss
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
            
            // Apply syntax highlighting
            if (window.Prism) {
                Prism.highlightAll();
            }
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-robot"></i>
                    <h3>AI-Powered Suggestions</h3>
                    <p>No AI suggestions available. Try analyzing more complex code.</p>
                </div>
            `;
        }
    }

    parseStructuredSuggestions(suggestions) {
        // Convert plain text suggestions into structured format
        return suggestions.map(suggestion => {
            // Parse suggestion text to extract structured information
            const lines = suggestion.split('\n').filter(line => line.trim());
            
            // Default structure
            let parsed = {
                title: 'Code Improvement Suggestion',
                description: suggestion,
                category: 'General',
                priority: 'medium',
                line: null,
                function: null,
                impact: 'Moderate performance improvement',
                fixes: [{
                    description: 'Apply the suggested changes to improve code quality',
                    code: null,
                    type: 'after'
                }],
                benefits: ['Improved code readability', 'Better performance', 'Reduced complexity']
            };
            
            // Try to extract more specific information
            if (suggestion.toLowerCase().includes('loop') || suggestion.toLowerCase().includes('iteration')) {
                parsed.category = 'Performance';
                parsed.title = 'Loop Optimization Needed';
                parsed.priority = 'high';
                parsed.impact = 'Significant performance improvement';
                parsed.fixes = [{
                    description: 'Replace nested loops with more efficient algorithms',
                    code: `# Instead of nested loops:\nfor i in range(n):\n    for j in range(n):\n        # O(n²) operation\n        \n# Use more efficient approach:\nresult = [process(item) for item in items]  # O(n)`,
                    type: 'after'
                }];
                parsed.benefits = ['Reduced time complexity', 'Better scalability', 'Lower CPU usage'];
            }
            
            if (suggestion.toLowerCase().includes('memory') || suggestion.toLowerCase().includes('cache')) {
                parsed.category = 'Memory';
                parsed.title = 'Memory Usage Optimization';
                parsed.priority = 'high';
                parsed.impact = 'Reduced memory consumption';
                parsed.fixes = [{
                    description: 'Implement proper memory management and caching strategies',
                    code: `# Use generators for large datasets:\ndef process_large_data():\n    for item in large_dataset:\n        yield process(item)  # Memory efficient\n        \n# Clear unused variables:\ndel large_variable\ngc.collect()`,
                    type: 'after'
                }];
                parsed.benefits = ['Lower memory footprint', 'Prevented memory leaks', 'Better resource utilization'];
            }
            
            if (suggestion.toLowerCase().includes('function') || suggestion.toLowerCase().includes('method')) {
                parsed.category = 'Code Structure';
                parsed.title = 'Function Refactoring Required';
                parsed.priority = 'medium';
                parsed.impact = 'Improved code maintainability';
                parsed.fixes = [{
                    description: 'Break down large functions into smaller, focused methods',
                    code: `# Instead of one large function:\ndef large_function(data):\n    # 50+ lines of code\n    pass\n    \n# Break into smaller functions:\ndef validate_data(data):\n    # validation logic\n    pass\n    \ndef process_data(data):\n    # processing logic\n    pass\n    \ndef save_results(results):\n    # saving logic\n    pass`,
                    type: 'after'
                }];
                parsed.benefits = ['Better code organization', 'Easier testing', 'Improved reusability'];
            }
            
            return parsed;
        });
    }

    getPriorityIcon(priority) {
        switch(priority) {
            case 'high': return 'fa-exclamation-triangle';
            case 'medium': return 'fa-exclamation-circle';
            case 'low': return 'fa-info-circle';
            default: return 'fa-lightbulb';
        }
    }

    copyCodeExample(button) {
        const codeBlock = button.closest('.code-example').querySelector('code');
        navigator.clipboard.writeText(codeBlock.textContent).then(() => {
            this.showSuccess('Code example copied to clipboard!');
            button.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });
    }

    applyFix(suggestionIndex) {
        this.showSuccess('Fix applied! Check the refactored code tab.');
        // Here you could implement actual code application logic
    }

    showMoreInfo(suggestionIndex) {
        // Show detailed information modal or expand section
        this.showSuccess('More detailed information would be shown here.');
    }

    dismissSuggestion(suggestionIndex) {
        const suggestionCard = document.querySelectorAll('.suggestion-card')[suggestionIndex];
        suggestionCard.style.opacity = '0.5';
        suggestionCard.style.pointerEvents = 'none';
        this.showSuccess('Suggestion dismissed.');
    }

    displayRefactoredCode(code) {
        const container = document.getElementById('refactoredCode');
        
        if (code && code.trim()) {
            container.innerHTML = `
                <pre><code class="language-python">${this.escapeHtml(code)}</code></pre>
            `;
            
            // Apply syntax highlighting
            if (window.Prism) {
                Prism.highlightAll();
            }
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-magic"></i>
                    <h3>Refactored Code</h3>
                    <p>No refactored code available</p>
                </div>
            `;
        }
    }

    updateCharts(data) {
        // Update complexity chart
        const complexityData = this.analyzeComplexityDistribution(data);
        this.charts.complexity.data.datasets[0].data = complexityData;
        this.charts.complexity.update();

        // Update issue distribution chart
        const issueData = this.analyzeIssueDistribution(data);
        this.charts.issues.data.datasets[0].data = issueData;
        this.charts.issues.update();

        // Update trend chart
        this.updateTrendChart(data);
        
        // Update performance score
        this.updatePerformanceScore(data);
    }

    analyzeComplexityDistribution(data) {
        // Simple complexity analysis based on issues found
        const totalIssues = (data.inefficiencies?.length || 0) + 
                           (data.bottlenecks?.length || 0) + 
                           (data.performance_hotspots?.length || 0);
        
        if (totalIssues === 0) return [100, 0, 0];
        if (totalIssues <= 3) return [70, 30, 0];
        if (totalIssues <= 6) return [30, 50, 20];
        return [10, 30, 60];
    }

    analyzeIssueDistribution(data) {
        return [
            data.performance_hotspots?.length || 0,
            data.inefficiencies?.filter(i => i.includes('memory')).length || 0,
            data.bottlenecks?.length || 0,
            data.inefficiencies?.filter(i => !i.includes('memory')).length || 0
        ];
    }

    updateTrendChart(data) {
        const now = new Date().toLocaleTimeString();
        const score = this.calculateQualityScore(data);
        
        this.charts.trend.data.labels.push(now);
        this.charts.trend.data.datasets[0].data.push(score);
        
        // Keep only last 10 data points
        if (this.charts.trend.data.labels.length > 10) {
            this.charts.trend.data.labels.shift();
            this.charts.trend.data.datasets[0].data.shift();
        }
        
        this.charts.trend.update();
    }

    calculateQualityScore(data) {
        const totalIssues = (data.inefficiencies?.length || 0) + 
                           (data.bottlenecks?.length || 0) + 
                           (data.performance_hotspots?.length || 0);
        
        return Math.max(0, 100 - (totalIssues * 10));
    }

    updatePerformanceScore(data) {
        const score = this.calculateQualityScore(data);
        const scoreElement = document.getElementById('performanceScore');
        const scoreValue = scoreElement.querySelector('.score-value');
        
        scoreValue.textContent = score;
        
        // Update circle progress
        const angle = (score / 100) * 360;
        scoreElement.style.setProperty('--score-angle', `${angle}deg`);
        
        // Update color based on score
        let color = '#dc3545'; // Red
        if (score >= 70) color = '#28a745'; // Green
        else if (score >= 40) color = '#ffc107'; // Yellow
        
        scoreElement.style.background = `conic-gradient(${color} 0deg, ${color} ${angle}deg, #e9ecef ${angle}deg)`;
    }

    updateStats() {
        document.getElementById('totalAnalyses').textContent = this.stats.totalAnalyses;
        document.getElementById('issuesFound').textContent = this.stats.issuesFound;
        document.getElementById('improvementScore').textContent = `${this.stats.improvementScore}%`;
    }

    switchTab(tabName) {
        // Remove active class from all tabs and panels
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        
        // Add active class to selected tab and panel
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}-panel`).classList.add('active');
    }

    copyRefactoredCode() {
        const codeElement = document.querySelector('#refactoredCode pre code');
        if (codeElement) {
            navigator.clipboard.writeText(codeElement.textContent).then(() => {
                this.showSuccess('Refactored code copied to clipboard!');
            });
        }
    }

    showLoading(message) {
        document.getElementById('loadingSpinner').querySelector('span').textContent = message;
        document.querySelector('.editor-overlay').classList.add('active');
    }

    hideLoading() {
        document.querySelector('.editor-overlay').classList.remove('active');
    }

    updateStatus(message, showProgress = false) {
        document.getElementById('statusText').textContent = message;
        const progressBar = document.getElementById('progressBar');
        
        if (showProgress) {
            progressBar.classList.add('active');
            // Simulate progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                }
                progressBar.querySelector('.progress-fill').style.width = `${progress}%`;
            }, 200);
        } else {
            progressBar.classList.remove('active');
            progressBar.querySelector('.progress-fill').style.width = '0%';
        }
        
        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (connected) {
            statusElement.className = 'status-indicator connected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> Connected';
        } else {
            statusElement.className = 'status-indicator disconnected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
        }
    }

    showError(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast error';
        toast.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    showSuccess(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast success';
        toast.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    clearResults() {
        document.getElementById('issuesList').innerHTML = '<p class="placeholder">No issues detected</p>';
        document.getElementById('hotspotsList').innerHTML = '<p class="placeholder">No hotspots detected</p>';
        document.getElementById('smellsList').innerHTML = '<p class="placeholder">No code smells detected</p>';
        document.getElementById('aiSuggestions').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-robot"></i>
                <h3>AI-Powered Suggestions</h3>
                <p>Run analysis to get intelligent refactoring suggestions</p>
            </div>
        `;
        document.getElementById('refactoredCode').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-magic"></i>
                <h3>Refactored Code</h3>
                <p>Your optimized code will appear here</p>
            </div>
        `;
        
        // Reset charts
        Object.values(this.charts).forEach(chart => {
            if (chart.data.datasets[0].data) {
                chart.data.datasets[0].data = chart.data.datasets[0].data.map(() => 0);
                chart.update();
            }
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HECSRefactoringApp();
});