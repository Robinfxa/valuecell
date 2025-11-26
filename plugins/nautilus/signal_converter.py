"""Signal Converter for Hybrid Decision Framework.

Converts between Nautilus trading signals and ValueCell trade instructions,
bridging the two systems with type-safe transformations.
"""

from typing import List, Optional
from loguru import logger

from valuecell.plugins.nautilus.signals import TradingSignal, SignalAction, SignalType


class SignalConverter:
    """Converts Nautilus signals to ValueCell instructions.
    
    Provides bidirectional conversion between Nautilus TradingSignal
    and ValueCell TradeInstruction formats.
    """
    
    def signals_to_instructions(
        self,
        signals: List[TradingSignal],
        compose_id: str
    ) -> List[dict]:
        """Convert Nautilus signals to ValueCell trade instructions.
        
        Args:
            signals: List of Nautilus trading signals
            compose_id: Compose cycle identifier from ValueCell
            
        Returns:
            List of TradeInstruction dictionaries
        """
        instructions = []
        
        for signal in signals:
            try:
                instruction = self._convert_single_signal(signal, compose_id)
                if instruction:
                    instructions.append(instruction)
            except Exception as e:
                logger.error(
                    "Failed to convert signal",
                    signal_id=signal.signal_id,
                    error=str(e)
                )
        
        logger.info(
            "Signal conversion",
            input_signals=len(signals),
            output_instructions=len(instructions)
        )
        
        return instructions
    
    def _convert_single_signal(
        self,
        signal: TradingSignal,
        compose_id: str
    ) -> Optional[dict]:
        """Convert single signal to instruction.
        
        Args:
            signal: Nautilus trading signal
            compose_id: Compose cycle ID
            
        Returns:
            TradeInstruction dict or None if conversion fails
        """
        # Convert action to side
        side = self._convert_action_to_side(signal.action)
        if not side:
            logger.warning(
                "Unsupported signal action",
                action=signal.action,
                signal_id=signal.signal_id
            )
            return None
        
        # Build instruction dictionary
        # Note: Using dict instead of importing ValueCell types to avoid circular deps
        instruction = {
            "instruction_id": signal.signal_id,
            "compose_id": compose_id,
            "instrument": {
                "symbol": signal.symbol
            },
            "side": side,
            "quantity": signal.quantity,
            "leverage": 1.0,  # Default no leverage
            "max_slippage_bps": 10,  # 0.1% default slippage
            "meta": {
                "signal_type": signal.signal_type.value,
                "strategy_id": signal.strategy_id,
                "reason": signal.reason,
                "confidence": signal.confidence,
                "source": "nautilus_strategy",
                "original_action": signal.action.value
            }
        }
        
        # Add price for limit orders
        if signal.order_type == "LIMIT" and signal.price:
            instruction["price"] = signal.price
        
        return instruction
    
    def _convert_action_to_side(self, action: SignalAction) -> Optional[str]:
        """Convert Nautilus action to ValueCell side.
        
        Args:
            action: Nautilus SignalAction
            
        Returns:
            ValueCell TradeSide string ("BUY"/"SELL") or None
        """
        if action == SignalAction.BUY:
            return "BUY"
        elif action == SignalAction.SELL:
            return "SELL"
        elif action in [SignalAction.CLOSE_LONG, SignalAction.CLOSE_SHORT]:
            # For close signals, we assume SELL to close long positions
            # In real implementation, need to check current position direction
            return "SELL"
        elif action == SignalAction.CLOSE_ALL:
            # Special handling needed - may generate multiple instructions
            logger.warning("CLOSE_ALL action requires special handling")
            return None
        else:
            return None
    
    def instruction_result_to_signal_result(
        self,
        tx_result: dict,
        original_signal: TradingSignal
    ) -> dict:
        """Convert ValueCell execution result back to Nautilus format.
        
        Args:
            tx_result: ValueCell TxResult
            original_signal: Original Nautilus signal
            
        Returns:
            SignalResult dictionary
        """
        return {
            "signal_id": original_signal.signal_id,
            "success": tx_result.get("status") == "FILLED",
            "order_id": tx_result.get("instruction_id"),
            "filled_quantity": tx_result.get("filled_qty", 0),
            "avg_price": tx_result.get("avg_exec_price"),
            "error_message": tx_result.get("error_msg"),
            "metadata": {
                "tx_status": tx_result.get("status"),
                "fee_cost": tx_result.get("fee_cost"),
                "timestamp": tx_result.get("ts")
            }
        }
