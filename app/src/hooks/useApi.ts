import { useState, useCallback } from 'react';

const API_BASE = 'http://localhost:8000/api/v1';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchData = useCallback(async (endpoint: string, options?: RequestInit) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setState({ data, loading: false, error: null });
      return data;
    } catch (err: any) {
      const errorMsg = err.message || 'Unknown error';
      setState({ data: null, loading: false, error: errorMsg });
      return null;
    }
  }, []);

  return { ...state, fetchData };
}

export async function getAgents() {
  const res = await fetch(`${API_BASE}/agents`);
  if (!res.ok) throw new Error('Failed to fetch agents');
  return res.json();
}

export async function getAgent(agentId: string) {
  const res = await fetch(`${API_BASE}/agents/${agentId}`);
  if (!res.ok) throw new Error('Failed to fetch agent');
  return res.json();
}

export async function getVitals() {
  const res = await fetch(`${API_BASE}/guardian/vitals`);
  if (!res.ok) throw new Error('Failed to fetch vitals');
  return res.json();
}

export async function getHealingLog(limit = 100) {
  const res = await fetch(`${API_BASE}/guardian/healing-log?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch healing log');
  return res.json();
}

export async function getConsciousnessScores() {
  const res = await fetch(`${API_BASE}/guardian/consciousness`);
  if (!res.ok) throw new Error('Failed to fetch consciousness scores');
  return res.json();
}

export async function getRiskEvents() {
  const res = await fetch(`${API_BASE}/risk/events`);
  if (!res.ok) throw new Error('Failed to fetch risk events');
  return res.json();
}

export async function getDashboard(period = '24h') {
  const res = await fetch(`${API_BASE}/analytics/dashboard?period=${period}`);
  if (!res.ok) throw new Error('Failed to fetch dashboard');
  return res.json();
}

export async function getTrends(days = 30) {
  const res = await fetch(`${API_BASE}/analytics/trends?days=${days}`);
  if (!res.ok) throw new Error('Failed to fetch trends');
  return res.json();
}

export async function sendChat(message: string, context?: Record<string, any>) {
  const res = await fetch(`${API_BASE}/swarm/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, user_id: 'web_user', priority: 'medium', context: context || {} }),
  });
  if (!res.ok) throw new Error('Failed to send chat');
  return res.json();
}

export async function chatWithAgent(agentId: string, query: string, context?: Record<string, any>) {
  const res = await fetch(`${API_BASE}/agents/${agentId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ agent_id: agentId, query, context: context || {} }),
  });
  if (!res.ok) throw new Error('Failed to chat with agent');
  return res.json();
}

export async function getDemoScenarios() {
  const res = await fetch(`${API_BASE}/demos/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch demo scenarios');
  return res.json();
}

export async function runDemoScenario(scenarioId: string) {
  const res = await fetch(`${API_BASE}/demos/run/${scenarioId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to run demo');
  return res.json();
}
