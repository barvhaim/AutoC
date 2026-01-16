# Multi-Agent System Architecture

## Overview

AutoC has been transformed into a hybrid multi-agent system that combines **LangGraph** for workflow orchestration with specialized **intelligent agents** for task execution. This architecture provides improved performance through parallel execution, better modularity, and enhanced maintainability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     LangGraph Orchestration Layer               │
│                    (Workflow & State Management)                │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
         ┌──────────▼──────────┐   ┌─────────▼──────────┐
         │   Sequential Phase  │   │   Parallel Phase   │
         │    (Phase 1 & 3)    │   │     (Phase 2)      │
         └──────────┬──────────┘   └─────────┬──────────┘
                    │                        │
    ┌───────────────┼────────────────────────┼───────────────-┐
    │               │                        │                │
┌───▼────┐   ┌─────▼──────┐   ┌──────────────▼─────────┐      │
│ Parser │   │ Enrichment │   │  Parallel Execution     │     │
│ Agent  │   │   Agent    │   │  (ThreadPoolExecutor)   │     │
└────────┘   └────────────┘   └──────────┬──────────────┘     │
                                          │                   │
                          ┌───────────────┼────────────┐      │
                          │               │            │      │
                    ┌─────▼──────┐ ┌─────▼─────┐ ┌───▼────┐   │
                    │  Keywords  │ │    IOC    │ │  QnA   │   │
                    │   Agent    │ │   Hunter  │ │ Agent  │   │
                    └────────────┘ └───────────┘ └────────┘   │
                                                              │
                                          ┌───────────────────┘
                                          │
                                    ┌─────▼──────┐
                                    │   MITRE    │
                                    │   Agent    │
                                    └────────────┘
```

## System Components

### 1. LangGraph Orchestration Layer

**Purpose**: Manages workflow execution, state transitions, and agent coordination.

**Key Features**:
- State management using TypedDict-based `PipelineState`
- Node-based workflow with conditional routing
- Error handling and recovery
- Integration with agent system

**Files**:
- [`backend/pipeline/agent_graph.py`](../backend/pipeline/agent_graph.py) - Hybrid workflow graph
- [`backend/pipeline/agent_nodes.py`](../backend/pipeline/agent_nodes.py) - Agent-enabled nodes
- [`backend/pipeline/state.py`](../backend/pipeline/state.py) - State definitions

### 2. Agent Manager

**Purpose**: Centralized management of agent lifecycle and execution.

**Key Features**:
- Singleton pattern for global agent registry
- Parallel execution using ThreadPoolExecutor
- Timeout management per agent
- Graceful error handling

**File**: [`backend/agents/agent_manager.py`](../backend/agents/agent_manager.py)

**Key Methods**:
```python
# Execute single agent with timeout
execute_agent(agent_name, task_description, context, timeout)

# Execute multiple agents in parallel
execute_parallel(tasks, fail_fast=False)
```

### 3. Specialized Agents

#### Parser Agent
**Role**: Content extraction specialist  
**Tools**: Docling parser, Crawl4AI parser  
**Execution**: Sequential (Phase 1)  
**File**: [`backend/agents/parser_agent.py`](../backend/agents/parser_agent.py)

#### Keywords Agent
**Role**: Security keyword identification  
**Tools**: Keyword search tool  
**Execution**: Parallel (Phase 2)  
**File**: [`backend/agents/keywords_agent.py`](../backend/agents/keywords_agent.py)

#### IOC Hunter Agent
**Role**: Indicator of Compromise extraction  
**Tools**: LLM-based IOC extractor  
**Execution**: Parallel (Phase 2)  
**File**: [`backend/agents/ioc_hunter_agent.py`](../backend/agents/ioc_hunter_agent.py)

#### QnA Agent
**Role**: Analyst question answering  
**Tools**: LLM with RAG support  
**Execution**: Parallel (Phase 2)  
**File**: [`backend/agents/qna_agent.py`](../backend/agents/qna_agent.py)

#### Enrichment Agent
**Role**: IOC threat intelligence enrichment  
**Tools**: VirusTotal API integration  
**Execution**: Sequential (Phase 3)  
**File**: [`backend/agents/enrichment_agent.py`](../backend/agents/enrichment_agent.py)

#### MITRE Agent
**Role**: ATT&CK framework classification  
**Tools**: ML-based TTP classifier  
**Execution**: Sequential (Phase 3)  
**File**: [`backend/agents/mitre_agent.py`](../backend/agents/mitre_agent.py)

### 4. Tool Layer

**Purpose**: Wrapper functions around existing extractors for agent use.

**Files**:
- [`backend/agents/tools/parser_tools.py`](../backend/agents/tools/parser_tools.py)
- [`backend/agents/tools/keywords_tools.py`](../backend/agents/tools/keywords_tools.py)
- [`backend/agents/tools/ioc_tools.py`](../backend/agents/tools/ioc_tools.py)
- [`backend/agents/tools/enrichment_tools.py`](../backend/agents/tools/enrichment_tools.py)
- [`backend/agents/tools/qna_tools.py`](../backend/agents/tools/qna_tools.py)
- [`backend/agents/tools/mitre_tools.py`](../backend/agents/tools/mitre_tools.py)

## Execution Flow

### Phase 1: Content Extraction (Sequential)
```
URL Input → Parser Agent → Textual Content
```

### Phase 2: Parallel Analysis
```
Content → ┌─ Keywords Agent → Keywords
          ├─ IOC Hunter Agent → IOCs
          └─ QnA Agent → Answers
```
**Performance**: ~40% faster than sequential execution

### Phase 3: Enrichment & Classification (Sequential)
```
IOCs → Enrichment Agent → Enriched IOCs
Content → MITRE Agent → TTPs
```

## Configuration

### Environment Variables

```bash
# Enable/disable agent system
USE_AGENT_SYSTEM=true

# Parallel execution settings
AGENT_PARALLEL_WORKERS=3
AGENT_ENABLE_PARALLEL=true

# Per-agent timeouts (seconds)
AGENT_TIMEOUT_PARSER=60
AGENT_TIMEOUT_KEYWORDS=30
AGENT_TIMEOUT_IOC=120
AGENT_TIMEOUT_ENRICHMENT=90
AGENT_TIMEOUT_QNA=60
AGENT_TIMEOUT_MITRE=45
```

### Toggling Between Systems

**Agent-based pipeline** (default):
```bash
USE_AGENT_SYSTEM=true
```

**Traditional pipeline**:
```bash
USE_AGENT_SYSTEM=false
```

## Error Handling

### Retry Logic
- Automatic retry with exponential backoff
- Configurable max retries (default: 3)
- Wait time: 2^attempt seconds

### Graceful Degradation
- Failed agents don't block workflow
- Partial results returned when possible
- Comprehensive error logging

### Timeout Management
- Per-agent timeout configuration
- Prevents hanging on slow operations
- Automatic cleanup on timeout

## Performance Characteristics

### Parallel Execution Benefits
- **Keywords Agent**: ~0.1s (keyword matching)
- **IOC Hunter Agent**: ~30-60s (LLM extraction)
- **QnA Agent**: ~10-30s (LLM Q&A)

**Sequential**: 40-90s total  
**Parallel**: 30-60s total (40% improvement)

### Resource Usage
- ThreadPoolExecutor with 3 workers (configurable)
- Memory-efficient state sharing
- Minimal overhead from agent abstraction

## Monitoring & Logging

### Agent Lifecycle Events
```python
INFO:backend.agents.base_agent:Agent 'parser' initialized successfully
INFO:backend.agents.base_agent:Agent 'parser' starting task: Extract content
INFO:backend.agents.base_agent:Agent 'parser' completed successfully in 5.04s
```

### Parallel Execution Tracking
```python
INFO:backend.agents.agent_manager:Executing 3 agents in parallel
INFO:backend.agents.agent_manager:Agent 'keywords' completed successfully
INFO:backend.agents.agent_manager:Agent 'ioc_hunter' completed successfully
INFO:backend.agents.agent_manager:Agent 'qna' completed successfully
```

### Error Tracking
```python
ERROR:backend.agents.base_agent:Agent 'ioc_hunter' failed (attempt 1/3): Connection timeout
INFO:backend.agents.base_agent:Retrying in 2s...
```

## Comparison: Traditional vs Multi-Agent

| Aspect | Traditional Pipeline | Multi-Agent System |
|--------|---------------------|-------------------|
| **Execution** | Sequential | Hybrid (Sequential + Parallel) |
| **Performance** | Baseline | 40% faster |
| **Modularity** | Monolithic nodes | Specialized agents |
| **Error Handling** | Basic | Advanced with retry |
| **Scalability** | Limited | High (parallel execution) |
| **Maintainability** | Moderate | High (separation of concerns) |
| **Testing** | Integration-focused | Unit + Integration |
