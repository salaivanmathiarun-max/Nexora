import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { 
  BarChart3, 
  Table, 
  Award, 
  Grid, 
  CheckCircle2, 
  Sparkles 
} from 'lucide-react';

const BenchmarkModal = () => {
  const [benchmarkData, setBenchmarkData] = useState(null);

  useEffect(() => {
    api.getBenchmarks()
      .then(data => setBenchmarkData(data))
      .catch(err => console.error(err));
  }, []);

  if (!benchmarkData) {
    return (
      <div className="w-full glass-panel rounded-2xl p-8 text-center text-slate-400">
        Loading research benchmark data...
      </div>
    );
  }

  const comparison = benchmarkData.comparison_matrix || [];
  const confusion = benchmarkData.confusion_matrix_sample || { labels: [], matrix: [] };

  return (
    <div className="w-full space-y-6 animate-fade-in">
      
      {/* Header */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <BarChart3 className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white font-['Outfit']">
              Research Paper Quantitative Evaluation (Section 4)
            </h2>
            <p className="text-xs text-slate-400">
              Benchmarked on the Samarkand v2 landmark dataset across 12 categories
            </p>
          </div>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
          The proposed <strong>Nexora Multimodal Framework</strong> achieves <strong>96.40% Accuracy</strong>, outperforming standard vision baselines by fusing multimodal feature representations with contextual metadata.
        </p>
      </div>

      {/* Model Performance Comparison Table (Section 4.4) */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-white font-['Outfit']">
          <Table className="w-4 h-4 text-teal-400" />
          <span>Quantitative Comparison Matrix (Table 1 in Paper)</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300 border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4">Model Architecture</th>
                <th className="py-3 px-4">Citation</th>
                <th className="py-3 px-4 text-right">Accuracy (%)</th>
                <th className="py-3 px-4 text-right">Precision (%)</th>
                <th className="py-3 px-4 text-right">Recall (%)</th>
                <th className="py-3 px-4 text-right">F1-Score (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {comparison.map((row, idx) => {
                const isOurs = row.model.includes('Nexora');
                return (
                  <tr 
                    key={idx}
                    className={`transition-colors ${
                      isOurs 
                        ? 'bg-teal-500/10 text-teal-200 font-bold border-l-4 border-l-teal-400' 
                        : 'hover:bg-slate-900/60'
                    }`}
                  >
                    <td className="py-3 px-4 font-sans font-semibold text-slate-200 flex items-center gap-2">
                      {isOurs && <Award className="w-4 h-4 text-teal-400 shrink-0" />}
                      <span>{row.model}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-sans">{row.citation}</td>
                    <td className="py-3 px-4 text-right">{row.accuracy.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right">{row.precision.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right">{row.recall.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right font-bold text-teal-300">{row.f1_score.toFixed(2)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Comparative Performance Bar Chart */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-white font-['Outfit']">
          <BarChart3 className="w-4 h-4 text-cyan-400" />
          <span>Comparative Accuracy Progression</span>
        </div>

        <div className="space-y-3 pt-2">
          {comparison.map((row, idx) => {
            const isOurs = row.model.includes('Nexora');
            return (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className={`font-medium ${isOurs ? 'text-teal-300 font-bold' : 'text-slate-300'}`}>
                    {row.model}
                  </span>
                  <span className="font-mono font-bold text-slate-200">{row.accuracy}%</span>
                </div>
                <div className="w-full h-3 rounded-full bg-slate-900 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      isOurs 
                        ? 'bg-gradient-to-r from-teal-400 to-cyan-400 shadow-md shadow-teal-500/30' 
                        : 'bg-slate-700'
                    }`}
                    style={{ width: `${(row.accuracy - 80) * 5}%` }} // normalized scale from 80% to 100%
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Confusion Matrix (Section 4.6 in Paper) */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-white font-['Outfit']">
          <Grid className="w-4 h-4 text-indigo-400" />
          <span>Landmark Classification Confusion Matrix (Section 4.6 Sample)</span>
        </div>
        <p className="text-xs text-slate-400">
          Diagonal cells denote ground-truth true positives. Off-diagonal denotes cross-monument feature misclassifications.
        </p>

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-center text-xs text-slate-300 border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold text-[11px]">
                <th className="py-2.5 px-3 text-left">Actual \ Predicted</th>
                {confusion.labels.map((lbl, i) => (
                  <th key={i} className="py-2.5 px-3 font-mono">{lbl}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {confusion.matrix.map((row, rIdx) => (
                <tr key={rIdx}>
                  <td className="py-2.5 px-3 text-left font-sans font-semibold text-slate-300">
                    {confusion.labels[rIdx]}
                  </td>
                  {row.map((val, cIdx) => {
                    const isDiagonal = rIdx === cIdx;
                    return (
                      <td 
                        key={cIdx} 
                        className={`py-2.5 px-3 font-bold ${
                          isDiagonal 
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' 
                            : val > 0 
                              ? 'text-amber-400' 
                              : 'text-slate-600'
                        }`}
                      >
                        {val}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default BenchmarkModal;
