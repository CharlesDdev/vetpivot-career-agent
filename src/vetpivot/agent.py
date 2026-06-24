"""ADK entrypoint.

Google ADK discovers a `root_agent` object from an `agent.py` module. The
project CLI does not import this module, so local mock behavior stays unchanged.
"""

from __future__ import annotations

from vetpivot.adk_agents import root_agent

