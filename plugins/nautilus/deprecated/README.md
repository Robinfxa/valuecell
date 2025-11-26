# Deprecated Files

This directory contains deprecated modules that have been superseded by ValueCell's native functionality.

## Deprecated Modules

### real_valuecell_bridge.py
**Status**: Deprecated as of Phase 8  
**Reason**: ValueCell provides native `CCXTExecutionGateway` for live trading  
**Replacement**: Use `valuecell.agents.common.trading.execution.ccxt_trading.CCXTExecutionGateway`

**Migration**:
```python
# Old (deprecated)
from valuecell.plugins.nautilus.real_valuecell_bridge import RealValueCellBridge
bridge = RealValueCellBridge(...)

# New (recommended)
# ValueCell handles execution internally through TradingConfig
```

### real_data_adapters.py
**Status**: Deprecated as of Phase 8  
**Reason**: ValueCell provides native `SimpleMarketDataSource` with CCXT  
**Replacement**: Use `valuecell.agents.common.trading.data.market.SimpleMarketDataSource`

**Migration**:
```python
# Old (deprecated)
from valuecell.plugins.nautilus.real_data_adapters import YFinanceAdapter, CCXTAdapter

# New (recommended)
# ValueCell handles data fetching internally through FeaturesPipeline
```

## Retained for Compatibility

The following modules are kept for backward compatibility but should not be used in new code:
- `execution_wrapper.py` - Use ValueCell's ExecutionGateway
- `plugin_service.py` - Use ValueCell's BaseStrategyAgent

## Phase 8 Architecture

Phase 8 introduces the **Hybrid Decision Framework** which fully integrates with ValueCell's infrastructure:

```
User Request → HybridComposer → Strategy Selection → ValueCell Execution
                  ↓
            StrategyRegistry
            SignalConverter
```

**Benefits**:
- Leverages ValueCell's battle-tested execution
- Automatic risk management
- Persistent portfolio tracking
- Integrated with ValueCell UI

**See**: `docs/VALUECELL_FEATURE_ANALYSIS.md` for detailed migration guide
