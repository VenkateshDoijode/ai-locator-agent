"""

Author: Venkateshwara Doijode

"""
import time                  # Used to measure wall-clock execution time of each agent
from functools import wraps  # Preserves the original function's metadata (name, docstring, etc.)
                             # when it is wrapped by a decorator
from utils.logger import logger  # Import the shared named logger defined in logger.py


def agent(name):
    """
    A parameterized decorator factory for agent functions.
    
    Usage:
        @agent("My Agent Name")
        def my_agent(state):
            ...

    Wraps any agent function to automatically:
      - Log when the agent starts
      - Log when the agent finishes, including how long it took
    
    Args:
        name (str): A human-readable label for the agent, used in log messages.
    
    Returns:
        decorator: A decorator that wraps the target agent function.
    """

    def decorator(func):
        """
        The actual decorator — receives the agent function (func) and returns
        a wrapped version of it with logging behavior injected around it.
        """

        @wraps(func)  # Ensures func's __name__, __doc__, etc. are preserved on the wrapper
        def wrapper(state):
            """
            The wrapper replaces the original function call.
            It runs logging + timing logic around the real agent function.
            
            Args:
                state (dict): The shared pipeline state passed between all agents.
            
            Returns:
                result: Whatever the original agent function returns (updated state).
            """

            # Log that this agent is beginning execution
            logger.info(f"[AGENT START] {name}")

            # Record the timestamp just before the agent function runs
            start = time.time()

            # Call the actual agent function with the pipeline state
            result = func(state)

            # Record the timestamp immediately after the agent finishes
            end = time.time()

            # Log completion along with the elapsed time, formatted to 2 decimal places
            logger.info(f"[AGENT END] {name} ({end-start:.2f}s)")

            # Return the agent's result (updated state) back to the pipeline
            return result

        return wrapper  # Return the wrapped function in place of the original

    return decorator  # Return the decorator so @agent("name") syntax works