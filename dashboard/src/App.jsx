import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, Activity, Shield, Zap, Search, 
  AlertTriangle, CheckCircle, Info, ChevronRight, Layers,
  Trash2, Download, Terminal
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const App = () => {
  const [dockerfile, setDockerfile] = useState('');
  const [lintResults, setLintResults] = useState([]);
  const [imageName, setImageName] = useState('');
  const [analysisReport, setAnalysisReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLint = async () => {
    if (!dockerfile.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.post('/api/lint', { dockerfile_content: dockerfile });
      setLintResults(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!imageName.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/analyze', { image_name: imageName });
      setAnalysisReport(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Make sure the image is built locally.');
      setAnalysisReport(null);
    } finally {
      setIsLoading(false);
    }
  };

  const chartData = analysisReport ? {
    labels: analysisReport.largest_layers.map((_, i) => `Layer ${i + 1}`),
    datasets: [
      {
        label: 'Size (MB)',
        data: analysisReport.largest_layers.map(l => (l.Size / (1024 * 1024)).toFixed(2)),
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
    ],
  } : null;

  return (
    <div className="container">
      <header className="header">
        <div className="logo">
          <Layers size={32} className="icon-blue" />
          <h1>Docker Slim Analyzer</h1>
        </div>
        <p>Optimize your container lifecycle with deep layer insights and static analysis.</p>
      </header>

      <div className="grid">
        {/* Linter Section */}
        <section className="card">
          <div className="card-header">
            <Shield className="icon-blue" />
            <h2>Dockerfile Static Linter</h2>
          </div>
          <div className="card-body">
            <textarea
              className="dockerfile-input"
              placeholder="# Paste your Dockerfile here..."
              value={dockerfile}
              onChange={(e) => setDockerfile(e.target.value)}
            />
            <button className="btn-primary" onClick={handleLint} disabled={isLoading}>
              {isLoading ? 'Analyzing...' : 'Run Audit'}
            </button>

            {lintResults.length > 0 && (
              <div className="lint-results">
                <h3>Issues Found ({lintResults.length})</h3>
                {lintResults.map((result, idx) => (
                  <div key={idx} className={`lint-item ${result.severity}`}>
                    <AlertTriangle size={16} />
                    <span><strong>Line {result.line}:</strong> {result.message}</span>
                  </div>
                ))}
              </div>
            )}
            {lintResults.length === 0 && dockerfile && !isLoading && (
              <div className="lint-success">
                <CheckCircle size={16} /> No major issues found!
              </div>
            )}
          </div>
        </section>

        {/* Analyzer Section */}
        <section className="card">
          <div className="card-header">
            <Activity className="icon-blue" />
            <h2>Image Layer Analysis</h2>
          </div>
          <div className="card-body">
            <div className="input-group">
              <input
                type="text"
                className="image-input"
                placeholder="Image Name (e.g. go-app:v1)"
                value={imageName}
                onChange={(e) => setImageName(e.target.value)}
              />
              <button className="btn-primary" onClick={handleAnalyze} disabled={isLoading}>
                {isLoading ? 'Analyzing...' : 'Inspect'}
              </button>
            </div>
            
            {error && <div className="error-msg">{error}</div>}

            {analysisReport && (
              <div className="report-view">
                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-label">Total Size</span>
                    <span className="stat-value">{analysisReport.total_size_mb} MB</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-label">Layers</span>
                    <span className="stat-value">{analysisReport.num_layers}</span>
                  </div>
                </div>

                <div className="chart-container">
                  <Bar 
                    data={chartData} 
                    options={{ 
                      responsive: true, 
                      maintainAspectRatio: false,
                      plugins: { legend: { display: false } }
                    }} 
                  />
                </div>

                <div className="layer-table-container">
                  <h3>Top Layers</h3>
                  <table className="layer-table">
                    <thead>
                      <tr>
                        <th>Size</th>
                        <th>Command</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysisReport.largest_layers.map((layer, i) => (
                        <tr key={i}>
                          <td>{(layer.Size / (1024 * 1024)).toFixed(2)} MB</td>
                          <td className="cmd-cell"><code>{layer.CreatedBy.substring(0, 100)}...</code></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </section>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .header { margin-bottom: 3rem; text-align: center; }
        .logo { display: flex; items-center: center; justify-content: center; gap: 1rem; margin-bottom: 0.5rem; }
        .logo h1 { font-size: 2.5rem; color: var(--text-main); }
        .header p { color: var(--text-dim); }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
        .card { background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border); overflow: hidden; height: fit-content; }
        .card-header { padding: 1.25rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 0.75rem; }
        .card-header h2 { font-size: 1.25rem; }
        .card-body { padding: 1.25rem; }
        
        .dockerfile-input { width: 100%; height: 300px; padding: 1rem; background: var(--bg-dark); color: #9cdcfe; border: 1px solid var(--border); border-radius: 8px; font-family: 'Terminal', monospace; margin-bottom: 1rem; resize: vertical; }
        .image-input { flex: 1; padding: 0.75rem; background: var(--bg-dark); border: 1px solid var(--border); border-radius: 8px; color: white; }
        .input-group { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
        
        .btn-primary { background: var(--primary); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
        .btn-primary:hover { background: var(--primary-dark); }
        .btn-primary:disabled { opacity: 0.5; }
        
        .lint-results { margin-top: 1.5rem; }
        .lint-item { padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.9rem; }
        .lint-item.warning { background: rgba(245, 158, 11, 0.1); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.2); }
        .lint-item.error { background: rgba(239, 68, 68, 0.1); color: var(--error); border: 1px solid rgba(239, 68, 68, 0.2); }
        .lint-success { color: var(--success); padding: 1rem; text-align: center; }
        
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; }
        .stat-card { background: var(--bg-dark); padding: 1rem; border-radius: 8px; text-align: center; }
        .stat-label { display: block; font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; margin-bottom: 0.25rem; }
        .stat-value { font-size: 1.5rem; font-weight: 700; color: var(--primary); }
        
        .chart-container { height: 250px; margin-bottom: 2rem; }
        .layer-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        .layer-table th { text-align: left; color: var(--text-dim); padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }
        .layer-table td { padding: 0.75rem 0; border-bottom: 1px solid var(--border); }
        .cmd-cell { max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--text-dim); }
        .cmd-cell code { background: rgba(0,0,0,0.2); padding: 0.1rem 0.3rem; border-radius: 4px; font-family: monospace; }
        
        .error-msg { color: var(--error); background: rgba(239, 68, 68, 0.1); padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
        .icon-blue { color: var(--primary); }

        @media (max-width: 968px) {
          .grid { grid-template-columns: 1fr; }
        }
      `}} />
    </div>
  );
};

export default App;
