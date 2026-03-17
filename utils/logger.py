"""

Author: Venkateshwara Doijode

"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("AgentPipeline")

# Standard library module for logging — provides flexible logging to console, files, etc.
import logging

# Configure the root logging system with global defaults.
# This affects all loggers unless they override these settings.
logging.basicConfig(
    level=logging.INFO,      # Minimum severity to capture: DEBUG < INFO < WARNING < ERROR < CRITICAL
                             # INFO means debug-level messages are ignored, but INFO and above are shown
    format="%(asctime)s | %(levelname)s | %(message)s"
    # Log line format:
    #   %(asctime)s   → human-readable timestamp (e.g. 2024-01-15 10:23:45,123)
    #   %(levelname)s → severity label (e.g. INFO, WARNING, ERROR)
    #   %(message)s   → the actual log message passed by the caller
)

# Create a named logger specifically for this project.
# Using a named logger (instead of the root logger) allows fine-grained control —
# e.g. you can later set different levels or handlers for "AgentPipeline" independently.
logger = logging.getLogger("AgentPipeline")