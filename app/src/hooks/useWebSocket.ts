/**
 * useWebSocket — Production-grade WebSocket hook for AfriSwarm.
 * Handles connection, reconnection, topic subscription, and typed messages.
 */
import { useCallback, useEffect, useRef, useState } from 'react';

export type WsMessageType =
  | 'connected'
  | 'vitals_update'
  | 'agent_update'
  | 'swarm_response'
  | 'alert'
  | 'ping';

export interface WsMessage<T = unknown> {
  type: WsMessageType;
  timestamp: string;
  data?: T;
  [key: string]: unknown;
}

interface UseWebSocketOptions {
  onMessage?: (msg: WsMessage) => void;
  onVitalsUpdate?: (data: VitalsData) => void;
  onAlert?: (data: AlertData) => void;
  onSwarmResponse?: (data: SwarmResponseData) => void;
  autoReconnect?: boolean;
  reconnectDelayMs?: number;
}

export interface VitalsData {
  overall_health: number;
  active_agents: number;
  total_agents: number;
  consciousness: number;
  tasks_in_progress: number;
  uptime_hours: number;
  agents: Record<string, AgentSnapshotData>;
}

export interface AgentSnapshotData {
  status: string;
  consciousness: number;
  tasks_completed: number;
  tasks_failed: number;
  avg_response_ms: number;
  uptime_seconds: number;
  consecutive_failures: number;
}

export interface AlertData {
  level: string;
  title: string;
  message: string;
  agent_id?: string;
}

export interface SwarmResponseData {
  response: Record<string, unknown>;
  agents_involved: string[];
}

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

const WS_BASE =
  import.meta.env.VITE_WS_URL ||
  `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/v1/ws`;

export function useSwarmWebSocket(clientId: string, options: UseWebSocketOptions = {}) {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastVitals, setLastVitals] = useState<VitalsData | null>(null);
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const {
    onMessage,
    onVitalsUpdate,
    onAlert,
    onSwarmResponse,
    autoReconnect = true,
    reconnectDelayMs = 3000,
  } = options;

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    const url = `${WS_BASE}/${clientId}`;
    setStatus('connecting');

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;
        setStatus('connected');
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          const msg: WsMessage = JSON.parse(event.data);
          onMessage?.(msg);

          switch (msg.type) {
            case 'vitals_update': {
              const vitals = msg.data as VitalsData;
              setLastVitals(vitals);
              onVitalsUpdate?.(vitals);
              break;
            }
            case 'alert': {
              const alert = msg.data as AlertData;
              setAlerts((prev) => [alert, ...prev].slice(0, 20));
              onAlert?.(alert);
              break;
            }
            case 'swarm_response': {
              onSwarmResponse?.(msg.data as SwarmResponseData);
              break;
            }
            case 'ping':
              ws.send(JSON.stringify({ type: 'pong' }));
              break;
          }
        } catch {
          // non-JSON frame, ignore
        }
      };

      ws.onerror = () => {
        if (!mountedRef.current) return;
        setStatus('error');
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setStatus('disconnected');
        if (autoReconnect) {
          reconnectTimer.current = setTimeout(connect, reconnectDelayMs);
        }
      };
    } catch {
      setStatus('error');
    }
  }, [clientId, onMessage, onVitalsUpdate, onAlert, onSwarmResponse, autoReconnect, reconnectDelayMs]);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((msg: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  return { status, lastVitals, alerts, sendMessage };
}
