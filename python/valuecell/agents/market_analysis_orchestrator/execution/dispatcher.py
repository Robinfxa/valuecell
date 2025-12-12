"""Execution Dispatcher for routing decisions to backends.

The dispatcher manages registered execution backends and routes
trading decisions from the Trader AI to the appropriate backend.
"""

from typing import Any, Dict, Optional

from loguru import logger

from .backends.base import ExecutionBackend, ExecutionDecision, ExecutionResult


class ExecutionDispatcher:
    """Dispatcher for routing execution decisions to registered backends.

    The dispatcher:
    1. Maintains a registry of available execution backends
    2. Generates prompts describing backend capabilities for Trader AI
    3. Routes decisions to the selected backend
    4. Handles fallback logic if a backend fails
    """

    def __init__(self):
        """Initialize dispatcher with empty backend registry."""
        self._backends: Dict[str, ExecutionBackend] = {}
        self._default_backend_id: Optional[str] = None

    def register_backend(self, backend: ExecutionBackend) -> None:
        """Register an execution backend.

        Args:
            backend: The backend instance to register
        """
        self._backends[backend.backend_id] = backend
        logger.info(
            "Registered execution backend",
            backend_id=backend.backend_id,
            name=backend.name,
        )

    def set_default_backend(self, backend_id: str) -> None:
        """Set the default backend for fallback.

        Args:
            backend_id: ID of the backend to use as default
        """
        if backend_id not in self._backends:
            raise ValueError(f"Backend not registered: {backend_id}")
        self._default_backend_id = backend_id

    def get_backend(self, backend_id: str) -> Optional[ExecutionBackend]:
        """Get a registered backend by ID.

        Args:
            backend_id: The backend ID

        Returns:
            The backend instance, or None if not found
        """
        return self._backends.get(backend_id)

    def list_backends(self) -> list[ExecutionBackend]:
        """List all registered backends.

        Returns:
            List of registered backend instances
        """
        return list(self._backends.values())

    def get_backends_prompt(self) -> str:
        """Generate a prompt section describing all available backends.

        This is used by the Trader AI to understand what execution
        options are available.

        Returns:
            Formatted prompt section
        """
        if not self._backends:
            return "No execution backends available."

        lines = ["AVAILABLE EXECUTION BACKENDS:"]
        for backend in self._backends.values():
            lines.append("")
            lines.append(backend.to_prompt_section())

        return "\n".join(lines)

    async def dispatch(
        self, decision: ExecutionDecision, context: Dict[str, Any]
    ) -> ExecutionResult:
        """Dispatch an execution decision to the selected backend.

        Args:
            decision: The execution decision from Trader AI
            context: Additional context (analysis, market data, etc.)

        Returns:
            ExecutionResult from the backend
        """
        backend = self._backends.get(decision.backend_id)

        if not backend:
            logger.warning(
                "Unknown backend requested, using default",
                requested=decision.backend_id,
                default=self._default_backend_id,
            )
            backend = self._backends.get(self._default_backend_id) if self._default_backend_id else None

            if not backend:
                return ExecutionResult(
                    success=False,
                    backend_id=decision.backend_id,
                    message=f"Unknown backend: {decision.backend_id}",
                )

        # Check if backend supports this decision
        if not backend.supports(decision):
            logger.warning(
                "Backend does not support decision",
                backend_id=decision.backend_id,
                action=decision.action,
            )
            return ExecutionResult(
                success=False,
                backend_id=decision.backend_id,
                message=f"Backend {decision.backend_id} does not support this decision type",
            )

        # Execute
        try:
            logger.info(
                "Dispatching to backend",
                backend_id=backend.backend_id,
                action=decision.action,
                symbol=decision.symbol,
            )
            result = await backend.execute(decision, context)
            logger.info(
                "Execution completed",
                backend_id=backend.backend_id,
                success=result.success,
                trades_count=len(result.trades),
            )
            return result

        except Exception as e:
            logger.exception(
                "Backend execution failed",
                backend_id=backend.backend_id,
                error=str(e),
            )
            return ExecutionResult(
                success=False,
                backend_id=backend.backend_id,
                message=f"Execution failed: {e}",
                metadata={"error": str(e)},
            )
