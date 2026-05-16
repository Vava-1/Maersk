# AfriSwarm Maersk Resilience Swarm v1.0.0

## The World's Most Advanced Autonomous Multi-Agent System for Global Shipping & Logistics

AfriSwarm is a production-grade, enterprise-class autonomous multi-agent swarm built for Maersk-level global shipping and logistics operations. It features 14 persistent, hyper-specialized AI agents that work together as a cohesive intelligence, coordinated by a supreme Orchestrator and protected by an ever-vigilant System Guardian.

---

## System Architecture

```
AfriSwarm Architecture
======================

                    [ User Interface - React 19 ]
                              |
                    [ FastAPI + WebSocket Gateway ]
                              |
              [ Orchestrator Agent - Master Coordinator ]
               /    |    |    |    |    |    |    |    \
    [Guardian] [Risk] [Route] [Compliance] [ESG] [Supplier]
         |                                              |
    [Healing Loop]                              [Inventory] [Incident]
                                                      |         |
                                              [Data] [Analytics] [Africa]
                                                  |       |        |
                                          [Security] [Knowledge]
```

---

## The 14 Agents

| # | Agent | ID | Role |
|---|-------|-----|------|
| 1 | **Orchestrator** | `orchestrator` | Master task coordinator with ROI estimation |
| 2 | **System Guardian** | `guardian` | Self-healing, monitoring, consciousness scoring |
| 3 | **Geopolitical Risk** | `geopolitical_risk` | Global disruption scanning |
| 4 | **Route Optimizer** | `route_optimizer` | Multi-modal route optimization |
| 5 | **Compliance** | `compliance` | Regulatory validation & audit |
| 6 | **ESG & Sustainability** | `esg` | Carbon tracking & green alternatives |
| 7 | **Supplier Risk** | `supplier_risk` | Multi-tier supplier monitoring |
| 8 | **Inventory Forecaster** | `inventory_forecaster` | Demand prediction & optimization |
| 9 | **Incident Response** | `incident_response` | Exception handling & workflows |
| 10 | **Data Integration** | `data_integration` | Multimodal data processing |
| 11 | **Analytics** | `analytics` | ROI dashboards & metrics |
| 12 | **Africa Specialist** | `africa_specialist` | African corridor expertise |
| 13 | **Security Guardian** | `security_audit` | Threat detection & audit trails |
| 14 | **Knowledge** | `knowledge` | Long-term memory & learning |

---

## Technology Stack

### Backend
- **Python 3.12+** with FastAPI
- **LangGraph** - Stateful agent graphs with persistence
- **Pydantic** - Type-safe schemas for all messages
- **PostgreSQL + PGVector** - Relational & vector storage
- **Redis** - Caching & pub/sub
- **Kafka** - Event streaming
- **Neo4j** - Knowledge graph

### Frontend
- **React 19** + TypeScript + Vite
- **Tailwind CSS** + shadcn/ui
- **Recharts** - Data visualization
- **Lucide** - Icon system

### Infrastructure
- **Docker** + docker-compose
- **Kubernetes** with HPA
- **Prometheus** + **Grafana**
- **Ollama** (optional) - Local LLM support

---

## Quick Start

### Prerequisites
- Docker 24+ and docker-compose
- 8GB+ RAM (16GB recommended with LLM)
- Ports: 8000, 3000, 5432, 6379, 9092, 9090

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd afriswarm

# Start all services
docker-compose up -d

# With local LLM support
docker-compose --profile llm up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f afriswarm
```

The application will be available at:
- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/afriswarm-grafana-2026)
- **Prometheus**: http://localhost:9090

### Option 2: Kubernetes

```bash
# Create namespace and secrets
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy database layer
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Deploy the application
kubectl apply -f k8s/afriswarm-app.yaml
kubectl apply -f k8s/network-policy.yaml

# Check deployment
kubectl get pods -n afriswarm
kubectl logs -f deployment/afriswarm-app -n afriswarm
```

### Option 3: Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd ..
npm install
npm run dev
```

---

## API Authentication

Default credentials for demo (change in production):

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `afriswarm2026` |
| Operator | `operator` | `operator2026` |

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"afriswarm2026"}'

# Use the returned token:
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/agents
```

---

## Demo Scenarios

AfriSwarm includes 5 pre-built demo scenarios:

1. **Red Sea Shipping Crisis** - Route rerouting via Cape of Good Hope
2. **EU CBAM Compliance Check** - Carbon border adjustment verification
3. **Africa Route Optimization** - Mombasa corridor optimization
4. **Port Congestion Incident** - Durban congestion response
5. **Supplier Risk Alert** - Lagos supplier assessment

Run from the UI or via API:
```bash
curl -X POST http://localhost:8000/api/v1/demos/run/red_sea_crisis
```

---

## Configuration

All configuration is managed via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://... | PostgreSQL connection |
| `REDIS_URL` | redis://redis:6379/0 | Redis connection |
| `KAFKA_BOOTSTRAP_SERVERS` | kafka:9092 | Kafka brokers |
| `SECRET_KEY` | (auto-generated) | JWT signing key |
| `LLM_PROVIDER` | local | LLM backend |
| `LOCAL_MODEL_URL` | http://localhost:11434 | Ollama endpoint |
| `WORKERS` | 4 | Uvicorn workers |

See `backend/app/config.py` for the complete configuration schema.

---

## Security Features

- **RBAC** - Role-based access control (admin, operator, analyst, viewer, guardian)
- **JWT Authentication** - Secure token-based auth
- **Cryptographic Audit Signing** - Tamper-proof audit logs
- **PII Redaction** - Automatic PII detection and redaction
- **Network Policies** - Kubernetes network isolation
- **Data Sovereignty** - On-prem deployment support
- **Rate Limiting** - API rate limiting per endpoint

---

## Monitoring & Observability

### Health Endpoints
- `GET /health` - Basic health check
- `GET /api/v1/status` - Full swarm status
- `GET /api/v1/guardian/vitals` - System vitals
- `GET /api/v1/guardian/consciousness` - Agent consciousness scores

### Prometheus Metrics
- Agent health scores
- Task throughput and latency
- Healing actions performed
- Error rates by agent
- System resource usage

### Grafana Dashboards
Pre-configured dashboards for:
- Swarm overview
- Agent performance
- Guardian health
- ROI metrics

---

## Project Structure

```
afriswarm/
├── backend/
│   ├── app/
│   │   ├── agents/           # All 14 agent implementations
│   │   ├── graphs/           # LangGraph orchestration
│   │   ├── services/         # WebSocket, memory, health
│   │   ├── utils/            # Logging, security
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration
│   │   └── state.py          # State schemas
│   ├── requirements.txt
│   └── Dockerfile
├── src/                      # React frontend
│   ├── components/
│   ├── sections/             # All views
│   ├── hooks/                # API hooks
│   ├── types/                # TypeScript types
│   └── App.tsx
├── k8s/                      # Kubernetes manifests
├── docs/                     # Documentation
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## License

Copyright AfriSwarm 2026. All rights reserved.

This system is built for demonstration and educational purposes.
Maersk is a registered trademark of A.P. Moller - Maersk A/S.

---

## Support

For issues, questions, or contributions:
- Create an issue in the repository
- Contact: afriswarm@example.com
