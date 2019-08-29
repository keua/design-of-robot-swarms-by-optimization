__author__ = "Jonas Kuckling, jonas.kuckling@ulb.ac.be"
"""
This module provides the following functionality
- execution.ExecutorFactory: a factory class that can be used to obtain an executor object
- execution.AutoMoDeExecutor: the abstract class that provides the execution logic

How to use the executor?
import execution.ExecutorFactory
executor = execution.ExecutorFactory.get_executor()
scores = executor.evaluate_controller(controller)
executor.advance_seeds()
"""

from execution.automode_executor import ExecutorFactory
