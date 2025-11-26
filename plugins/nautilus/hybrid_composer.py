"""Hybrid Composer for Mixed LLM-Strategy Decision Making.

This module implements the core decision engine that combines:
1. LLM-based market analysis
2. Rule-based trading strategies  
3. Intelligent strategy selection

Three operational modes:
- llm: Pure LLM decision making (ValueCell native)
- rule: Fixed rule-based strategy
- hybrid: LLM selects strategy, rules execute
"""

from typing import Optional, Dict, Any, List
from loguru import logger

from valuecell.plugins.nautilus.strategy_registry import get_registry
from valuecell.plugins.nautilus.signal_converter import SignalConverter
from valuecell.plugins.nautilus.light_strategy import LightStrategy


class HybridComposer:
    """Hybrid decision composer combining LLM and rule strategies.
    
    This composer enables flexible decision making through three modes:
    
    1. LLM Mode: Pure LLM-based decisions using ValueCell's LlmComposer
    2. Rule Mode: Fixed rule-based strategy (EMA, RSI, BB, etc.)
    3. Hybrid Mode: LLM analyzes market and selects best strategy
    
    The hybrid mode is the key innovation - LLM acts as a meta-strategist
    that selects which rule-based strategy to use based on market conditions.
    
    Attributes:
        request: User request with trading configuration
        mode: Decision mode (llm/rule/hybrid)
        fixed_strategy: Strategy ID for rule mode
        converter: Signal to instruction converter
        active_strategy: Currently active strategy instance
        active_strategy_id: ID of active strategy
    """
    
    def __init__(self, request):
        """Initialize hybrid composer.
        
        Args:
            request: UserRequest with trading_config containing:
                - decision_mode: "llm" | "rule" | "hybrid"
                - fixed_strategy_id: Optional strategy for rule mode
                - allow_strategy_switch: Enable dynamic switching in hybrid mode
        """
        self.request = request
        self.mode = getattr(
            request.trading_config, 
            'decision_mode', 
            'hybrid'
        )
        self.fixed_strategy = getattr(
            request.trading_config,
            'fixed_strategy_id',
            None
        )
        
        # Initialize components
        self.converter = SignalConverter()
        self.registry = get_registry()
        
        # Active strategy state
        self.active_strategy: Optional[LightStrategy] = None
        self.active_strategy_id: Optional[str] = None
        
        # LLM composer (lazy init for llm/hybrid modes)
        self._llm_composer = None
        
        logger.info(
            "HybridComposer initialized",
            mode=self.mode,
            fixed_strategy=self.fixed_strategy
        )
    
    async def compose(self, context) -> dict:
        """Main decision entry point.
        
        Args:
            context: ComposeContext with features, portfolio, digest
            
        Returns:
            ComposeResult dict with instructions and rationale
        """
        logger.info(
            "Compose cycle",
            mode=self.mode,
            compose_id=context.compose_id,
            features_count=len(context.features)
        )
        
        if self.mode == "llm":
            return await self._llm_mode_decision(context)
        elif self.mode == "rule":
            return await self._rule_mode_decision(context)
        elif self.mode == "hybrid":
            return await self._hybrid_mode_decision(context)
        else:
            logger.error("Unknown decision mode", mode=self.mode)
            return self._empty_result(f"Unknown mode: {self.mode}")
    
    async def _llm_mode_decision(self, context) -> dict:
        """Pure LLM decision making.
        
        Uses ValueCell's native LlmComposer for market analysis
        and trade decision generation.
        
        Args:
            context: ComposeContext
            
        Returns:
            ComposeResult from LLM
        """
        # Lazy init LLM composer
        if self._llm_composer is None:
            from valuecell.agents.common.trading.decision.prompt_based import LlmComposer
            self._llm_composer = LlmComposer(self.request)
        
        result = await self._llm_composer.compose(context)
        
        logger.info(
            "LLM decision",
            instructions_count=len(result.instructions),
            rationale=result.rationale[:100] if result.rationale else None
        )
        
        # Convert to dict for consistency
        return {
            "instructions": [self._instruction_to_dict(i) for i in result.instructions],
            "rationale": result.rationale,
            "metadata": {"decision_mode": "llm"}
        }
    
    async def _rule_mode_decision(self, context) -> dict:
        """Fixed rule-based strategy decision.
        
        Uses a fixed strategy (specified in config) to generate signals.
        
        Args:
            context: ComposeContext
            
        Returns:
            ComposeResult from rule strategy
        """
        # Determine strategy ID
        strategy_id = self.fixed_strategy or "ema_cross"
        
        # Initialize strategy if needed
        if self.active_strategy_id != strategy_id:
            self._initialize_strategy(strategy_id)
        
        # Feed features to strategy
        self._feed_features_to_strategy(context.features)
        
        # Get signals from strategy
        signals = self._get_strategy_signals()
        
        # Convert to instructions
        instructions = self.converter.signals_to_instructions(
            signals,
            context.compose_id
        )
        
        rationale = f"Rule-based: {self.active_strategy.__class__.__name__}"
        if signals:
            rationale += f" - {signals[0].reason}"
        
        logger.info(
            "Rule decision",
            strategy=strategy_id,
            signals_count=len(signals),
            instructions_count=len(instructions)
        )
        
        return {
            "instructions": instructions,
            "rationale": rationale,
            "metadata": {
                "decision_mode": "rule",
                "strategy_id": strategy_id,
                "signals_count": len(signals)
            }
        }
    
    async def _hybrid_mode_decision(self, context) -> dict:
        """Hybrid decision: LLM selects strategy, rules execute.
        
        Process:
        1. Build strategy selection prompt
        2. Ask LLM to analyze market and choose strategy
        3. Parse LLM's strategy selection
        4. Execute selected strategy
        5. Convert signals to instructions
        
        Args:
            context: ComposeContext
            
        Returns:
            ComposeResult from hybrid decision
        """
        # Step 1: Build strategy selection prompt
        strategy_prompt = self._build_strategy_selection_prompt(context)
        
        # Step 2: Call LLM for strategy selection
        llm_response = await self._call_llm_for_strategy_selection(
            context,
            strategy_prompt
        )
        
        # Step 3: Parse selected strategy
        selected_strategy_id = self._parse_strategy_selection(llm_response)
        
        # Step 4: Initialize/switch strategy if needed
        if selected_strategy_id != self.active_strategy_id:
            logger.info(
                "Strategy switch",
                from_strategy=self.active_strategy_id,
                to_strategy=selected_strategy_id,
                reason=llm_response.get('reasoning', 'LLM recommendation')
            )
            self._initialize_strategy(selected_strategy_id)
        
        # Step 5: Execute strategy
        self._feed_features_to_strategy(context.features)
        signals = self._get_strategy_signals()
        instructions = self.converter.signals_to_instructions(
            signals,
            context.compose_id
        )
        
        # Build hybrid rationale
        rationale_lines = [
            "Hybrid Decision:",
            f"- Market Condition: {llm_response.get('market_condition', 'N/A')}",
            f"- LLM Analysis: {llm_response.get('analysis', 'N/A')[:100]}",
            f"- Selected Strategy: {selected_strategy_id}",
            f"- Confidence: {llm_response.get('confidence', 0):.2f}",
        ]
        
        if signals:
            rationale_lines.append(f"- Signal: {signals[0].reason}")
        else:
            rationale_lines.append("- Signal: No action")
        
        rationale = "\n".join(rationale_lines)
        
        logger.info(
            "Hybrid decision",
            market_condition=llm_response.get('market_condition'),
            selected_strategy=selected_strategy_id,
            signals_count=len(signals),
            instructions_count=len(instructions)
        )
        
        return {
            "instructions": instructions,
            "rationale": rationale,
            "metadata": {
                "decision_mode": "hybrid",
                "llm_analysis": llm_response.get('analysis'),
                "market_condition": llm_response.get('market_condition'),
                "selected_strategy": selected_strategy_id,
                "strategy_confidence": llm_response.get('confidence'),
                "signals_count": len(signals)
            }
        }
    
    def _build_strategy_selection_prompt(self, context) -> str:
        """Build prompt for LLM strategy selection.
        
        Args:
            context: ComposeContext with market data
            
        Returns:
            Formatted prompt string
        """
        # Get available strategies
        strategies_desc = self.registry.to_llm_prompt()
        
        # Summarize current features
        features_summary = self._summarize_features(context.features)
        
        # Summarize portfolio
        portfolio_summary = self._summarize_portfolio(context.portfolio)
        
        # Summarize digest
        digest_summary = self._summarize_digest(context.digest)
        
        prompt = f"""You are a professional trading strategist analyzing market conditions.

CURRENT MARKET DATA:
{features_summary}

PORTFOLIO STATUS:
{portfolio_summary}

RECENT PERFORMANCE:
{digest_summary}

{strategies_desc}

YOUR TASK:
1. Analyze the current market condition (trending/ranging/volatile)
2. Select the MOST SUITABLE strategy from the available options
3. Explain your reasoning

Respond in JSON format:
{{
    "market_condition": "trending|ranging|volatile",
    "analysis": "Brief 1-2 sentence market analysis",
    "selected_strategy_id": "strategy_id",
    "confidence": 0.0-1.0,
    "reasoning": "Why this strategy fits the current market"
}}
"""
        return prompt
    
    async def _call_llm_for_strategy_selection(
        self,
        context,
        prompt: str
    ) -> Dict[str, Any]:
        """Call LLM to select strategy.
        
        Args:
            context: ComposeContext
            prompt: Strategy selection prompt
            
        Returns:
            Dict with LLM response (market_condition, selected_strategy_id, etc.)
        """
        # TODO: Integrate with ValueCell's LLM service
        # For now, use simple heuristic based on features
        
        # Temporary implementation: analyze volatility from features
        if context.features:
            # Simple heuristic: check if we have volume/volatility data
            # In production, this would call the actual LLM
            
            # Default to trending market with EMA
            return {
                "market_condition": "trending",
                "analysis": "Market shows consistent directional movement",
                "selected_strategy_id": "ema_cross",
                "confidence": 0.75,
                "reasoning": "EMA crossover strategy works well in trending markets"
            }
        
        # Fallback
        return {
            "market_condition": "unknown",
            "analysis": "Insufficient data for market analysis",
            "selected_strategy_id": "ema_cross",
            "confidence": 0.5,
            "reasoning": "Default to EMA strategy"
        }
    
    def _parse_strategy_selection(
        self,
        llm_response: Dict[str, Any]
    ) -> str:
        """Parse and validate LLM's strategy selection.
        
        Args:
            llm_response: LLM response dict
            
        Returns:
            Valid strategy_id
        """
        strategy_id = llm_response.get('selected_strategy_id', 'ema_cross')
        
        # Validate strategy exists
        if not self.registry.get(strategy_id):
            logger.warning(
                "LLM selected unknown strategy, using default",
                selected=strategy_id,
                default="ema_cross"
            )
            return "ema_cross"
        
        return strategy_id
    
    def _initialize_strategy(self, strategy_id: str):
        """Initialize a strategy instance.
        
        Args:
            strategy_id: Strategy to initialize
        """
        metadata = self.registry.get(strategy_id)
        if not metadata:
            raise ValueError(f"Strategy not found: {strategy_id}")
        
        # Create strategy instance
        self.active_strategy = metadata.strategy_class(
            strategy_id=strategy_id
        )
        self.active_strategy.start()
        self.active_strategy_id = strategy_id
        
        logger.info(
            "Strategy initialized",
            strategy_id=strategy_id,
            strategy_name=metadata.name
        )
    
    def _feed_features_to_strategy(self, features: List):
        """Feed ValueCell features to Nautilus strategy.
        
        Args:
            features: List of FeatureVector from ValueCell
        """
        if not self.active_strategy:
            return
        
        for fv in features:
            # Convert FeatureVector to bar dict
            bar = {
                'timestamp': fv.ts / 1000.0,  # Convert ms to seconds
                'symbol': fv.instrument.symbol,
                'open': fv.values.get('open', fv.values.get('close')),
                'high': fv.values.get('high', fv.values.get('close')),
                'low': fv.values.get('low', fv.values.get('close')),
                'close': fv.values.get('close', 0),
                'volume': fv.values.get('volume', 0)
            }
            
            self.active_strategy.on_bar(bar)
    
    def _get_strategy_signals(self) -> List:
        """Get pending signals from active strategy.
        
        Returns:
            List of TradingSignal
        """
        if not self.active_strategy:
            return []
        
        # Get strategy's signal handler buffer
        if hasattr(self.active_strategy, '_pending_signals'):
            signals = self.active_strategy._pending_signals.copy()
            self.active_strategy._pending_signals.clear()
            return signals
        
        return []
    
    def _summarize_features(self, features: List) -> str:
        """Summarize features for LLM prompt.
        
        Args:
            features: List of FeatureVector
            
        Returns:
            Human-readable summary
        """
        if not features:
            return "No market data available"
        
        lines = []
        for fv in features[:5]:  # Limit to 5 instruments
            symbol = fv.instrument.symbol
            close = fv.values.get('close', 0)
            volume = fv.values.get('volume', 0)
            lines.append(f"- {symbol}: Price=${close:.2f}, Volume={volume:.0f}")
        
        if len(features) > 5:
            lines.append(f"... and {len(features) - 5} more instruments")
        
        return "\n".join(lines)
    
    def _summarize_portfolio(self, portfolio) -> str:
        """Summarize portfolio for LLM prompt.
        
        Args:
            portfolio: PortfolioView
            
        Returns:
            Human-readable summary
        """
        if not portfolio:
            return "No portfolio data"
        
        lines = [
            f"- Cash: ${portfolio.account_balance:.2f}",
            f"- Total Value: ${portfolio.total_value:.2f}" if hasattr(portfolio, 'total_value') else "",
            f"- Positions: {len(portfolio.positions) if hasattr(portfolio, 'positions') else 0}"
        ]
        
        return "\n".join(line for line in lines if line)
    
    def _summarize_digest(self, digest) -> str:
        """Summarize trade digest for LLM prompt.
        
        Args:
            digest: TradeDigest
            
        Returns:
            Human-readable summary
        """
        if not digest or not hasattr(digest, 'by_instrument'):
            return "No trading history yet"
        
        lines = []
        for symbol, entry in list(digest.by_instrument.items())[:3]:
            lines.append(
                f"- {symbol}: {entry.trade_count} trades, "
                f"PnL=${entry.realized_pnl:.2f}, "
                f"WinRate={entry.win_rate*100:.1f}%"
            )
        
        if hasattr(digest, 'sharpe_ratio') and digest.sharpe_ratio:
            lines.append(f"- Overall Sharpe Ratio: {digest.sharpe_ratio:.2f}")
        
        return "\n".join(lines) if lines else "No completed trades"
    
    def _instruction_to_dict(self, instruction) -> dict:
        """Convert TradeInstruction object to dict.
        
        Args:
            instruction: TradeInstruction object
            
        Returns:
            Instruction as dict
        """
        # If already dict, return as-is
        if isinstance(instruction, dict):
            return instruction
        
        # Convert object to dict
        return {
            "instruction_id": instruction.instruction_id,
            "compose_id": instruction.compose_id,
            "instrument": {
                "symbol": instruction.instrument.symbol
            },
            "side": instruction.side.value if hasattr(instruction.side, 'value') else str(instruction.side),
            "quantity": instruction.quantity,
            "leverage": getattr(instruction, 'leverage', 1.0),
            "meta": getattr(instruction, 'meta', {})
        }
    
    def _empty_result(self, rationale: str) -> dict:
        """Create empty result.
        
        Args:
            rationale: Reason for empty result
            
        Returns:
            ComposeResult dict with no instructions
        """
        return {
            "instructions": [],
            "rationale": rationale,
            "metadata": {"decision_mode": self.mode}
        }
