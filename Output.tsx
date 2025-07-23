import { useEffect, useState, useMemo } from "react";

import Header from "@/components/Header";
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from "@/components/ui/card";
import CombinedSummaryCard from "@/components/analysis/CombinedSummaryCard";
import ActionButtonsSection from "@/components/analysis/ActionButtonsSection";
import DisclaimerCard from "@/components/analysis/DisclaimerCard";
import ReactMarkdown from "react-markdown";
import { TrendingUp, BarChart3, PieChart, Target, AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";
import MultiPaneChart from "@/components/charts/MultiPaneChart";
import EnhancedMultiPaneChart from "@/components/charts/EnhancedMultiPaneChart";
import ChartDebugger from "@/components/charts/ChartDebugger";
import DataTester from "@/components/charts/DataTester";
import { Link } from "react-router-dom";
import { AnalysisData, ChartData, AnalysisResponse, isAnalysisResponse } from "@/types/analysis";
import { cleanText } from "@/utils/textCleaner";
import { ChartValidationResult } from "@/utils/chartUtils";
import { testChartData } from "@/utils/testData";





const timeframeOptions = [
  { value: '7d', label: '7D' },
  { value: '30d', label: '30D' },
  { value: '90d', label: '3M' },
  { value: '180d', label: '6M' },
  { value: '1y', label: '1Y' },
  { value: 'all', label: 'All' },
];

const Output: React.FC = () => {
  const [rawData, setRawData] = useState<ChartData[]>([]);
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [stockSymbol, setStockSymbol] = useState<string>("");
  const [selectedTimeframe, setSelectedTimeframe] = useState('all'); // Default to 'all'
  const [validationResult, setValidationResult] = useState<ChartValidationResult | null>(null);
  const [chartStats, setChartStats] = useState<any>(null);
  const [showDebug, setShowDebug] = useState(false);

  // --- Filter data by timeframe ---
  const filteredRawData = useMemo(() => {
    if (selectedTimeframe === 'all') return rawData;
    const now = new Date();
    const days = {
      '7d': 7,
      '30d': 30,
      '90d': 90,
      '180d': 180,
      '1y': 365,
    }[selectedTimeframe] || 0;
    const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
    return rawData.filter(item => new Date(item.date) >= cutoffDate);
  }, [rawData, selectedTimeframe]);

  // --- price stats
  const stats = useMemo(() => {
    if (rawData.length < 2) return null;
    const prev = rawData[rawData.length - 2];
    const last = rawData[rawData.length - 1];
    const delta = last.close - prev.close;
    const deltaPct = prev.close ? (delta / prev.close) * 100 : 0;
    return {
      lastClose: last.close,
      lastVolume: last.volume,
      lastDate: last.date,
      delta,
      deltaPct,
    };
  }, [rawData]);

  // --- Calculate mean, peak, and lowest close values for filteredRawData ---
  const summaryStats = useMemo(() => {
    if (!filteredRawData || filteredRawData.length === 0) return null;
    const closes = filteredRawData.map(d => d.close);
    const mean = closes.reduce((sum, v) => sum + v, 0) / closes.length;
    const max = Math.max(...closes);
    const min = Math.min(...closes);
    const current = closes[closes.length - 1];
    return {
      mean,
      max,
      min,
      current,
      distFromMean: current - mean,
      distFromMax: current - max,
      distFromMin: current - min,
      distFromMeanPct: mean !== 0 ? ((current - mean) / mean) * 100 : 0,
      distFromMaxPct: max !== 0 ? ((current - max) / max) * 100 : 0,
      distFromMinPct: min !== 0 ? ((current - min) / min) * 100 : 0,
    };
  }, [filteredRawData]);

  useEffect(() => {
    const storedData = localStorage.getItem("analysisResult");
    if (storedData) {
      try {
        const parsedData = JSON.parse(storedData);
        console.log("Raw parsed data:", parsedData);

        let results: AnalysisData;
        let data: ChartData[];

        if (isAnalysisResponse(parsedData)) {
          console.log("Using new API response format");
          setStockSymbol(parsedData.stock_symbol);
          results = parsedData.results;
          data = parsedData.data || [];
        } else {
          console.log("Using legacy data format");
          results = parsedData.results;
          data = parsedData.data || [];
          setStockSymbol("STOCK"); // Fallback for legacy data
        }

        // Clean text fields in the results
        const cleanedResults: AnalysisData = {
          ...results,
          indicator_summary_md: cleanText(results.indicator_summary_md || ''),
          chart_insights: cleanText(results.chart_insights || ''),
          consensus: {
            ...results.consensus,
            signal_details: results.consensus?.signal_details?.map((detail: any) => ({
              ...detail,
              description: cleanText(detail.description || '')
            })) || []
          },
          ai_analysis: {
            ...results.ai_analysis,
            short_term: {
              ...results.ai_analysis?.short_term,
              rationale: cleanText(results.ai_analysis?.short_term?.rationale || '')
            },
            medium_term: {
              ...results.ai_analysis?.medium_term,
              rationale: cleanText(results.ai_analysis?.medium_term?.rationale || '')
            },
            long_term: {
              ...results.ai_analysis?.long_term,
              rationale: cleanText(results.ai_analysis?.long_term?.rationale || '')
            }
          }
        };

        setAnalysisData(cleanedResults);

        const validatedData = (data || []).filter(d =>
          d && typeof d === 'object' &&
          typeof d.date === 'string' &&
          !isNaN(new Date(d.date).getTime()) &&
          ['open', 'high', 'low', 'close', 'volume'].every(key => typeof d[key] === 'number' && Number.isFinite(d[key]))
        );
        setRawData(validatedData);

      } catch (error) {
        console.error("Error parsing analysis data from localStorage:", error);
        setAnalysisData(null);
        setRawData([]);
      }
    }
  }, []);

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <Header />
        <div className="mx-auto px-4 py-8 max-w-screen-2xl">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-slate-800 mb-4">No Analysis Data</h1>
            <p className="text-lg text-slate-600 mb-8">Please run an analysis first.</p>
            <Link to="/analysis">
              <Button className="bg-emerald-500 hover:bg-emerald-600 text-white">
                Start New Analysis
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { consensus, indicators, ai_analysis } = analysisData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Header />
      
      <div className="mx-auto px-4 py-8 max-w-screen-2xl">
        {/* Stock Symbol Header */}
        {stockSymbol && (
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-slate-800 mb-2">
              {stockSymbol} - Technical Analysis
            </h1>
            <p className="text-slate-600">Detailed price action and technical indicators</p>
          </div>
        )}

        {/* Analysis Summary FIRST */}
        <div className="mb-8 lg:col-span-2">
          <CombinedSummaryCard 
            consensus={consensus} 
            indicators={indicators} 
            aiAnalysis={ai_analysis}
            latestPrice={stats?.lastClose ?? null}
            summaryStats={summaryStats}
          />           
        </div>

        {/* AI Analysis Section SECOND */}
        <div className="mb-8 lg:col-span-2">
          <Card className="mb-8 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-t-lg">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-6 w-6" />
                <CardTitle className="text-xl">AI Trading Analysis</CardTitle>
              </div>
              <CardDescription className="text-purple-100">
                AI-generated trading recommendations and risk assessment
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Short Term */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-slate-700 flex items-center">
                    <BarChart3 className="h-4 w-4 mr-2 text-blue-500" />
                    Short Term ({ai_analysis?.short_term?.horizon_days || 'N/A'} days)
                  </h3>
                  <div className="space-y-2">
                    <div className="bg-blue-50 p-3 rounded">
                      <div className="text-sm text-slate-600">Entry Range</div>
                      <div className="font-medium text-blue-700">
                        {ai_analysis?.short_term?.entry_range ? `₹${ai_analysis.short_term.entry_range[0]} - ₹${ai_analysis.short_term.entry_range[1]}` : 'N/A'}
                      </div>
                    </div>
                    <div className="bg-red-50 p-3 rounded">
                      <div className="text-sm text-slate-600">Stop Loss</div>
                      <div className="font-medium text-red-700">{ai_analysis?.short_term?.stop_loss ? `₹${ai_analysis.short_term.stop_loss}` : 'N/A'}</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded">
                      <div className="text-sm text-slate-600">Targets</div>
                      <div className="font-medium text-green-700">
                        {ai_analysis?.short_term?.targets ? `₹${ai_analysis.short_term.targets.join(', ₹')}` : 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Medium Term */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-slate-700 flex items-center">
                    <PieChart className="h-4 w-4 mr-2 text-orange-500" />
                    Medium Term ({ai_analysis?.medium_term?.horizon_days || 'N/A'} days)
                  </h3>
                  <div className="space-y-2">
                    <div className="bg-orange-50 p-3 rounded">
                      <div className="text-sm text-slate-600">Entry Range</div>
                      <div className="font-medium text-orange-700">
                        {ai_analysis?.medium_term?.entry_range ? `₹${ai_analysis.medium_term.entry_range[0]} - ₹${ai_analysis.medium_term.entry_range[1]}` : 'N/A'}
                      </div>
                    </div>
                    <div className="bg-red-50 p-3 rounded">
                      <div className="text-sm text-slate-600">Stop Loss</div>
                      <div className="font-medium text-red-700">{ai_analysis?.medium_term?.stop_loss ? `₹${ai_analysis.medium_term.stop_loss}` : 'N/A'}</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded">
                      <div className="text-sm text-slate-600">Targets</div>
                      <div className="font-medium text-green-700">
                        {ai_analysis?.medium_term?.targets ? `₹${ai_analysis.medium_term.targets.join(', ₹')}` : 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Long Term */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-slate-700 flex items-center">
                    <Target className="h-4 w-4 mr-2 text-purple-500" />
                    Long Term ({ai_analysis?.long_term?.horizon_days || 'N/A'} days)
                  </h3>
                  <div className="space-y-2">
                    <div className="bg-purple-50 p-3 rounded">
                      <div className="text-sm text-slate-600">Investment Rating</div>
                      <div className="font-medium text-purple-700">{ai_analysis?.long_term?.investment_rating || 'N/A'}</div>
                    </div>
                    <div className="bg-blue-50 p-3 rounded">
                      <div className="text-sm text-slate-600">Confidence</div>
                      <div className="font-medium text-blue-700">{ai_analysis?.confidence_pct ? `${ai_analysis?.confidence_pct}%` : 'N/A'}</div>
                    </div>
                    <div className="bg-emerald-50 p-3 rounded">
                      <div className="text-sm text-slate-600">Trend</div>
                      <div className="font-medium text-emerald-700">{ai_analysis?.trend || 'N/A'}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-8">
                <h3 className="font-semibold text-slate-700 flex items-center">
                  <AlertTriangle className="h-4 w-4 mr-2 text-red-500" />
                  Risk Assessment
                </h3>
                <div className="space-y-3 mt-4">
                  {ai_analysis?.risks?.map((risk, index) => (
                    <div key={index} className="flex items-start space-x-3 bg-red-50 p-4 rounded-lg">
                      <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
                      <p className="text-slate-700">{risk}</p>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="mb-12">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-slate-800">Price Chart</h2>
            <div className="flex items-center space-x-4">
              <div className="flex space-x-2 bg-white/50 rounded-lg p-1 shadow-sm border border-slate-200">
                {timeframeOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setSelectedTimeframe(option.value)}
                    className={`px-3 py-1 text-sm rounded-md transition-colors ${
                      selectedTimeframe === option.value
                        ? 'bg-blue-500 text-white'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDebug(!showDebug)}
                className="text-xs"
              >
                {showDebug ? 'Hide Debug' : 'Show Debug'}
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  console.log('=== Testing Current Data ===');
                  testChartData();
                  console.log('Current filtered data:', filteredRawData);
                }}
                className="text-xs"
              >
                Test Data
              </Button>
            </div>
          </div>
          
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm mb-8">
            <CardContent className="p-0">
              <div className="h-[1000px] w-full">
                <EnhancedMultiPaneChart 
                  data={filteredRawData} 
                  height={1000}
                  debug={showDebug}
                  onValidationResult={setValidationResult}
                  onStatsCalculated={setChartStats}
                />
              </div>
            </CardContent>
          </Card>
          
          {/* Data Tester Section */}
          <div className="mb-8">
            <DataTester data={filteredRawData} />
          </div>
          
          {/* Debug Section */}
          {showDebug && (
            <div className="mb-8">
              <ChartDebugger 
                data={filteredRawData}
                validationResult={validationResult}
                stats={chartStats}
                onRefresh={() => {
                  setValidationResult(null);
                  setChartStats(null);
                }}
              />
            </div>
          )}
        </div>

        {/* Remove grid for last two sections and stack vertically */}
        <div>
          {/* Must Watch Levels */}
          <Card className="mb-4 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-t-lg">
              <div className="flex items-center space-x-2">
                <Target className="h-6 w-6" />
                <CardTitle className="text-xl">Key Levels to Watch</CardTitle>
              </div>
              <CardDescription className="text-yellow-100">
                Critical price levels for decision making
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {ai_analysis?.must_watch_levels?.map((level, index) => (
                  <div key={index} className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-400">
                    <p className="text-slate-700 font-medium">{level}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Technical Indicators Summary */}
          <Card className="mb-8 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-t-lg">
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-6 w-6" />
                <CardTitle className="text-xl">Technical Analysis Summary</CardTitle>
              </div>
              <CardDescription className="text-blue-100">
                Comprehensive technical indicator analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="prose max-w-none">
                <ReactMarkdown>{analysisData.indicator_summary_md}</ReactMarkdown>
              </div>
            </CardContent>
          </Card>
        </div>

          {/* Action Buttons */}
          <div className="lg:col-span-2"><ActionButtonsSection /></div>
          
          {/* Disclaimer */}
          <div className="lg:col-span-2"><DisclaimerCard /></div>
      </div>
    </div>
  );
};

export default Output;
