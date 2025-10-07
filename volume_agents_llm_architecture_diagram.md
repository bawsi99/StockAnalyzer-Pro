# Volume Agents LLM Call Architecture

## Current Architecture Overview

The volume agents system uses **3 different LLM call patterns** depending on migration status:

```mermaid
graph TD
    A[VolumeAgentsOrchestrator._execute_agent] --> B{Agent Type?}
    
    B -->|LLM Agents| C[self.llm_agents[name].analyze_with_llm()]
    B -->|Backend/LLM| D[Technical Analysis + Chart + LLM Call in Orchestrator]
    B -->|Legacy| E[Technical Analysis + Chart + GeminiClient in Orchestrator]
    
    C --> C1[support_resistance: SupportResistanceLLMAgent]
    C --> C2[volume_confirmation: VolumeConfirmationLLMAgent]
    
    D --> D1[institutional_activity: backend/llm client]
    D --> D2[volume_momentum: backend/llm client]
    
    E --> E1[volume_anomaly: GeminiClient]
    
    C1 --> F1[Internal: Technical + Prompt + LLM]
    C2 --> F2[Internal: Technical + Prompt + LLM]
    
    D1 --> G1[Orchestrator: Technical + Prompt + LLM]
    D2 --> G2[Orchestrator: Technical + Prompt + LLM]
    
    E1 --> H1[Orchestrator: Technical + Prompt + Legacy LLM]
```

## Agent-by-Agent Breakdown

### 🎯 **Dedicated LLM Agents** (Self-Contained)
**Agents**: `support_resistance`, `volume_confirmation`

**LLM Call Location**: Inside the agent's own code
```python
# In volume_agents.py _execute_agent()
if agent_name in self.llm_agents:
    llm_agent_result = await self.llm_agents[agent_name].analyze_with_llm(
        stock_data=stock_data, 
        symbol=symbol, 
        chart_image=chart_image,
        context=""
    )
```

**What happens inside the agent**:
```python
# In support_resistance/llm_agent.py
async def analyze_with_llm(self, stock_data, symbol, chart_image, context):
    # 1. Technical analysis
    technical_analysis = self.processor.process_support_resistance_data(stock_data)
    
    # 2. Build comprehensive prompt
    prompt = self._build_comprehensive_prompt(symbol, technical_analysis, context)
    
    # 3. LLM call
    llm_analysis = await self.llm_client.generate(
        prompt=prompt,
        images=[chart_image] if chart_image else None
    )
    
    return {technical_analysis, llm_analysis, ...}
```

### 🔧 **Backend/LLM Clients** (Orchestrator-Handled)
**Agents**: `institutional_activity`, `volume_momentum`

**LLM Call Location**: In `volume_agents.py`
```python
# In volume_agents.py _execute_agent()
if agent_name in self.llm_clients and chart_image:
    prompt_text = self._build_agent_prompt_with_template(agent_name, analysis_data, symbol)
    
    llm_response = await self.llm_clients[agent_name].generate(
        prompt=prompt_text,
        images=[chart_image],
        enable_code_execution=True
    )
```

### 📜 **Legacy GeminiClient** (Orchestrator-Handled)
**Agents**: `volume_anomaly`

**LLM Call Location**: In `volume_agents.py`
```python
# In volume_agents.py _execute_agent()
if agent_client and chart_image:
    prompt_text = self._build_agent_prompt(agent_name, analysis_data, symbol)
    
    llm_response = await agent_client.analyze_volume_agent_specific(
        chart_image, prompt_text, agent_name
    )
```

## Summary Table

| Agent | LLM Framework | Call Location | Prompt Building | Technical Analysis |
|-------|---------------|---------------|-----------------|-------------------|
| `support_resistance` | `backend/llm` | **Agent Internal** | Agent Internal | Agent Internal |
| `volume_confirmation` | `backend/llm` | **Agent Internal** | Agent Internal | Agent Internal |
| `institutional_activity` | `backend/llm` | **Orchestrator** | Orchestrator | Orchestrator |
| `volume_momentum` | `backend/llm` | **Orchestrator** | Orchestrator | Orchestrator |
| `volume_anomaly` | `backend/gemini` | **Orchestrator** | Orchestrator | Orchestrator |

## Migration Benefits

**Dedicated LLM Agents** (like `support_resistance`) provide:
- ✅ Self-contained architecture
- ✅ Sophisticated internal prompt management
- ✅ Better separation of concerns
- ✅ Easier testing and debugging
- ✅ More sophisticated context engineering

**Orchestrator-handled agents** still rely on:
- 🔄 Central prompt building in `volume_agents.py`
- 🔄 Shared LLM calling logic
- 🔄 Less sophisticated prompt templates