"""Base agent class for all AutoC agents"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AutoC agents

    This class provides common functionality for all agents including:
    - Task execution with error handling
    - Retry logic with exponential backoff
    - Logging and monitoring
    """

    def __init__(
        self, name: str, role: str, goal: str, backstory: str, verbose: bool = True
    ):
        """Initialize base agent

        Args:
            name: Unique identifier for the agent
            role: Role description for the agent
            goal: Goal the agent is trying to achieve
            backstory: Background story for the agent
            verbose: Whether to enable verbose logging
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        logger.info("Agent '%s' initialized successfully", self.name)

    def execute(
        self, task_description: str, context: Dict[str, Any], max_retries: int = 3
    ) -> Any:
        """Execute a task with this agent

        Args:
            task_description: Description of the task to execute
            context: Context data needed for task execution
            max_retries: Maximum number of retry attempts

        Returns:
            Task execution result

        Raises:
            Exception: If task execution fails after all retries
        """
        logger.info("Agent '%s' starting task: %s", self.name, task_description)

        for attempt in range(max_retries):
            try:
                start_time = time.time()
                result = self._execute_internal(task_description, context)
                execution_time = time.time() - start_time

                logger.info(
                    "Agent '%s' completed successfully in %.2fs",
                    self.name,
                    execution_time,
                )
                return result

            except Exception as e:
                logger.error(
                    "Agent '%s' failed (attempt %s/%s): %s",
                    self.name,
                    attempt + 1,
                    max_retries,
                    str(e),
                )

                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2**attempt
                    logger.info("Retrying in %ss...", wait_time)
                    time.sleep(wait_time)
                else:
                    logger.error(
                        "Agent '%s' failed after %s attempts", self.name, max_retries
                    )
                    raise

    @abstractmethod
    def _execute_internal(self, task_description: str, context: Dict[str, Any]) -> Any:
        """Internal execution logic to be implemented by subclasses

        Args:
            task_description: Description of the task
            context: Context data for execution

        Returns:
            Execution result
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}')>"
