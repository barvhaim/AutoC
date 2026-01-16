"""Central manager for all agents in the AutoC system"""

from typing import Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import logging
from backend.agents.config import AgentConfig

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages all agents and their execution

    This class provides:
    - Agent registration and lifecycle management
    - Sequential and parallel task execution
    - Timeout handling
    - Result aggregation
    - Error handling and logging
    """

    def __init__(self, max_workers: Optional[int] = None):
        """Initialize the agent manager

        Args:
            max_workers: Maximum number of parallel workers (defaults to config)
        """
        self.agents: Dict[str, Any] = {}
        self.max_workers = max_workers or AgentConfig.MAX_WORKERS
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        logger.info(f"AgentManager initialized with {self.max_workers} workers")

    def register_agent(self, name: str, agent: Any):
        """Register an agent with the manager

        Args:
            name: Unique identifier for the agent
            agent: Agent instance to register
        """
        if name in self.agents:
            logger.warning(f"Agent '{name}' already registered, overwriting")

        self.agents[name] = agent
        logger.info(f"Registered agent: {name}")

    def get_agent(self, name: str) -> Optional[Any]:
        """Get a registered agent by name

        Args:
            name: Agent identifier

        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(name)

    def execute_agent(
        self,
        agent_name: str,
        task: str,
        context: Dict[str, Any],
        timeout: Optional[int] = None,
    ) -> Any:
        """Execute a single agent with timeout

        Args:
            agent_name: Name of the agent to execute
            task: Task description
            context: Context data for the task
            timeout: Timeout in seconds (defaults to agent-specific timeout)

        Returns:
            Task execution result

        Raises:
            ValueError: If agent not found
            TimeoutError: If execution exceeds timeout
            Exception: If execution fails
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")

        agent = self.agents[agent_name]
        timeout = timeout or AgentConfig.get_timeout(agent_name)

        logger.info(f"Executing agent '{agent_name}' with timeout {timeout}s")

        try:
            # Submit task with timeout
            future = self.executor.submit(agent.execute, task, context)
            result = future.result(timeout=timeout)
            return result

        except TimeoutError:
            logger.error(f"Agent '{agent_name}' timed out after {timeout}s")
            raise
        except Exception as e:
            logger.error(f"Agent '{agent_name}' execution failed: {str(e)}")
            raise

    def execute_parallel(
        self, tasks: Dict[str, Tuple[str, Dict[str, Any]]], fail_fast: bool = False
    ) -> Dict[str, Any]:
        """Execute multiple agents in parallel

        Args:
            tasks: Dict mapping agent_name to (task_description, context) tuple
            fail_fast: If True, stop on first failure; if False, continue and return None for failed tasks

        Returns:
            Dict mapping agent_name to result (or None if failed and fail_fast=False)

        Raises:
            Exception: If fail_fast=True and any agent fails
        """
        if not AgentConfig.PARALLEL_EXECUTION:
            logger.info("Parallel execution disabled, executing sequentially")
            return self._execute_sequential(tasks, fail_fast)

        logger.info(f"Executing {len(tasks)} agents in parallel")

        futures = {}
        for agent_name, (task_desc, context) in tasks.items():
            timeout = AgentConfig.get_timeout(agent_name)
            future = self.executor.submit(
                self._execute_with_timeout, agent_name, task_desc, context, timeout
            )
            futures[future] = agent_name

        results = {}
        for future in as_completed(futures):
            agent_name = futures[future]
            try:
                results[agent_name] = future.result()
                logger.info(f"Agent '{agent_name}' completed successfully")
            except Exception as e:
                logger.error(f"Agent '{agent_name}' failed: {str(e)}")
                if fail_fast:
                    # Cancel remaining tasks
                    for f in futures:
                        f.cancel()
                    raise
                else:
                    results[agent_name] = None

        return results

    def _execute_with_timeout(
        self, agent_name: str, task: str, context: Dict[str, Any], timeout: int
    ) -> Any:
        """Internal method to execute agent with timeout

        Args:
            agent_name: Name of the agent
            task: Task description
            context: Context data
            timeout: Timeout in seconds

        Returns:
            Execution result
        """
        agent = self.agents[agent_name]
        return agent.execute(task, context)

    def _execute_sequential(
        self, tasks: Dict[str, Tuple[str, Dict[str, Any]]], fail_fast: bool
    ) -> Dict[str, Any]:
        """Execute tasks sequentially

        Args:
            tasks: Dict mapping agent_name to (task_description, context) tuple
            fail_fast: If True, stop on first failure

        Returns:
            Dict mapping agent_name to result
        """
        results = {}
        for agent_name, (task_desc, context) in tasks.items():
            try:
                results[agent_name] = self.execute_agent(agent_name, task_desc, context)
            except Exception as e:
                logger.error(f"Agent '{agent_name}' failed: {str(e)}")
                if fail_fast:
                    raise
                else:
                    results[agent_name] = None

        return results

    def list_agents(self) -> list:
        """List all registered agents

        Returns:
            List of agent names
        """
        return list(self.agents.keys())

    def shutdown(self, wait: bool = True):
        """Shutdown the executor

        Args:
            wait: Whether to wait for pending tasks to complete
        """
        logger.info("Shutting down AgentManager")
        self.executor.shutdown(wait=wait)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()

    def __repr__(self) -> str:
        return f"<AgentManager(agents={len(self.agents)}, workers={self.max_workers})>"


# Made with Bob
