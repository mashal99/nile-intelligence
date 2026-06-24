'use client'
import { useEffect, useState } from 'react'
import { Sparkles, Send, Loader2, MessageCircle, TrendingUp, DollarSign } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { MarketInsight } from '@/types'
import Header from '@/components/layout/Header'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { formatDate } from '@/lib/utils'

const AREAS = [
  { value: '', label: 'All Egypt' },
  { value: 'new-cairo', label: 'New Cairo' },
  { value: 'sheikh-zayed', label: 'Sheikh Zayed' },
  { value: '6th-of-october', label: '6th of October' },
  { value: 'new-administrative-capital', label: 'New Capital' },
  { value: 'north-coast', label: 'North Coast' },
]

export default function AIInsightsPage() {
  const [insights, setInsights] = useState<MarketInsight[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [asking, setAsking] = useState(false)
  const [selectedArea, setSelectedArea] = useState('')
  const [budget, setBudget] = useState('')
  const [activeMode, setActiveMode] = useState<'ask' | 'generate' | 'invest'>('ask')

  useEffect(() => {
    api.get<{ results: MarketInsight[] }>('/market/insights/?limit=10')
      .then(r => setInsights(r.data.results || r.data as any))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const generateInsight = async () => {
    setGenerating(true)
    try {
      const { data } = await api.post('/ai/generate/', {
        type: 'weekly_summary',
        area_slug: selectedArea || undefined,
      })
      toast.success('Market insight generated!')
      setInsights(prev => [{
        id: Date.now(),
        insight_type: 'weekly_summary',
        title: data.title,
        summary: data.summary,
        area_name: null,
        tags: [],
        generated_at: new Date().toISOString(),
        valid_until: null,
      }, ...prev])
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to generate insight. Check your subscription plan.'
      toast.error(msg)
    } finally { setGenerating(false) }
  }

  const askQuestion = async () => {
    if (!question.trim()) return
    setAsking(true)
    setAnswer('')
    try {
      const { data } = await api.post('/ai/ask/', { question })
      setAnswer(data.answer)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to get answer. Check your subscription plan.')
    } finally { setAsking(false) }
  }

  const findOpportunities = async () => {
    if (!budget) { toast.error('Enter your budget'); return }
    setGenerating(true)
    setAnswer('')
    try {
      const { data } = await api.post('/ai/generate/', {
        type: 'investment_opportunities',
        budget_egp: budget,
      })
      setAnswer(data.opportunities)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to analyze. Check subscription.')
    } finally { setGenerating(false) }
  }

  return (
    <div className="flex flex-col flex-1">
      <Header title="AI Insights" subtitle="Claude-powered Egyptian real estate intelligence" />

      <div className="p-6 space-y-6">
        {/* Mode Selector */}
        <div className="flex gap-2 flex-wrap">
          {[
            { id: 'ask', label: 'Ask a Question', icon: MessageCircle },
            { id: 'generate', label: 'Generate Report', icon: Sparkles },
            { id: 'invest', label: 'Investment Finder', icon: DollarSign },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveMode(id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeMode === id ? 'bg-brand-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}
            >
              <Icon className="w-4 h-4" /> {label}
            </button>
          ))}
        </div>

        {/* Ask Mode */}
        {activeMode === 'ask' && (
          <Card>
            <CardHeader>
              <CardTitle>Ask the AI Market Expert</CardTitle>
            </CardHeader>
            <p className="text-sm text-gray-500 mb-4">
              Ask anything about the Egyptian real estate market — pricing, areas, developers, investment strategies.
            </p>
            <div className="flex gap-3">
              <input
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && askQuestion()}
                placeholder="e.g. What are the best areas for apartment investment under 3M EGP in 2024?"
                className="flex-1 text-sm border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <Button onClick={askQuestion} loading={asking} className="shrink-0">
                <Send className="w-4 h-4" />
              </Button>
            </div>
            {asking && (
              <div className="flex items-center gap-3 mt-4 text-gray-500 text-sm">
                <Loader2 className="w-4 h-4 animate-spin" />
                AI is analyzing market data...
              </div>
            )}
            {answer && (
              <div className="mt-4 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-4 h-4 text-brand-600" />
                  <span className="text-sm font-semibold text-brand-700">AI Analysis</span>
                </div>
                <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">{answer}</p>
              </div>
            )}
            {/* Suggested Questions */}
            <div className="mt-4">
              <p className="text-xs text-gray-400 mb-2">Try asking:</p>
              <div className="flex flex-wrap gap-2">
                {[
                  'What is the price trend in New Cairo?',
                  'Which developer has the best payment plans?',
                  'Is now a good time to buy in Sheikh Zayed?',
                  'Compare New Capital vs New Cairo for investment',
                ].map(q => (
                  <button key={q} onClick={() => setQuestion(q)} className="text-xs px-3 py-1.5 bg-gray-100 text-gray-600 rounded-full hover:bg-brand-50 hover:text-brand-700 transition-colors">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Generate Mode */}
        {activeMode === 'generate' && (
          <Card>
            <CardHeader>
              <CardTitle>Generate Weekly Market Summary</CardTitle>
            </CardHeader>
            <p className="text-sm text-gray-500 mb-4">
              AI analyzes current market data to produce a comprehensive market intelligence report.
            </p>
            <div className="flex gap-3 mb-4">
              <select
                value={selectedArea}
                onChange={e => setSelectedArea(e.target.value)}
                className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none"
              >
                {AREAS.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
              </select>
              <Button onClick={generateInsight} loading={generating}>
                <Sparkles className="w-4 h-4 mr-1.5" /> Generate Insight
              </Button>
            </div>
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700">
              Requires Professional or Enterprise plan. Uses ~1,500 AI tokens per generation.
            </div>
          </Card>
        )}

        {/* Investment Finder Mode */}
        {activeMode === 'invest' && (
          <Card>
            <CardHeader>
              <CardTitle>Investment Opportunity Finder</CardTitle>
            </CardHeader>
            <p className="text-sm text-gray-500 mb-4">
              AI identifies the best investment opportunities based on your budget and current market data.
            </p>
            <div className="flex gap-3 mb-4">
              <div className="flex-1">
                <label className="text-sm font-medium text-gray-700 mb-1 block">Budget (EGP)</label>
                <input
                  type="number"
                  value={budget}
                  onChange={e => setBudget(e.target.value)}
                  placeholder="e.g. 3000000"
                  className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div className="flex items-end">
                <Button onClick={findOpportunities} loading={generating}>
                  <TrendingUp className="w-4 h-4 mr-1.5" /> Find Opportunities
                </Button>
              </div>
            </div>
            {answer && (
              <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-100">
                <div className="flex items-center gap-2 mb-3">
                  <DollarSign className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-semibold text-green-700">Investment Analysis</span>
                </div>
                <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">{answer}</p>
              </div>
            )}
          </Card>
        )}

        {/* Previous Insights */}
        <Card>
          <CardHeader>
            <CardTitle>Previous AI Insights</CardTitle>
          </CardHeader>
          {loading ? (
            <div className="space-y-3">
              {Array(3).fill(0).map((_, i) => <div key={i} className="h-20 animate-pulse bg-gray-100 rounded-lg" />)}
            </div>
          ) : insights.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-40" />
              <p>No AI insights generated yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {insights.map(insight => (
                <div key={insight.id} className="p-4 border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-brand-500 flex-shrink-0" />
                        <span className="text-xs text-brand-600 font-medium">{insight.insight_type.replace(/_/g, ' ')}</span>
                        {insight.area_name && <span className="text-xs text-gray-400">· {insight.area_name}</span>}
                      </div>
                      <p className="font-semibold text-gray-900 text-sm mb-1">{insight.title}</p>
                      <p className="text-gray-500 text-xs line-clamp-3">{insight.summary}</p>
                    </div>
                    <span className="text-xs text-gray-400 whitespace-nowrap flex-shrink-0">{formatDate(insight.generated_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
