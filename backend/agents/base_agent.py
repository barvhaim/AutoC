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

    Note: This is a simplified agent that directly calls tool functions
    rather than using CrewAI's Agent class.
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
        logger.info(f"Agent '{self.name}' initialized successfully")

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
        logger.info(f"Agent '{self.name}' starting task: {task_description}")

        for attempt in range(max_retries):
            try:
                start_time = time.time()
                result = self._execute_internal(task_description, context)
                execution_time = time.time() - start_time

                logger.info(
                    f"Agent '{self.name}' completed successfully in {execution_time:.2f}s"
                )
                return result

            except Exception as e:
                logger.error(
                    f"Agent '{self.name}' failed (attempt {attempt + 1}/{max_retries}): {str(e)}"
                )

                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2**attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Agent '{self.name}' failed after {max_retries} attempts"
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
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}')>"


# Made with Bob
