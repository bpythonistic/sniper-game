"""
Signal Generator

This module provides a class for generating the sniper scope signal.
"""

from contextlib import contextmanager
from typing import Callable, Generator

import numpy as np


def generate_sine_function(
    frequency: float, amplitude: float, phase: float = 0.0
) -> Callable[[float], float]:
    """
    Generates a sine wave signal for the sniper scope.

    :param frequency: The frequency of the sine wave in Hz.
    :type frequency: float
    :param amplitude: The amplitude of the sine wave.
    :type amplitude: float
    :param phase: The phase shift of the sine wave in radians (default is 0).
    :type phase: float
    :return: A function that takes time (t) as input and
        returns the sine wave value at that time.
    :rtype: Callable[[float], float]
    """
    return lambda t: amplitude * np.sin(2 * np.pi * frequency * t + phase)


@contextmanager
def new_scope(
    amplitude: float, phase: float = 0.0
) -> Generator[Callable[[float], Callable[[float], float]], None, None]:
    """
    Context manager for the sniper scope signal generator.

    :param frequency: The frequency of the sine wave in Hz.
    :type frequency: float
    :param amplitude: The amplitude of the sine wave.
    :type amplitude: float
    :param phase: The phase shift of the sine wave in radians (default is 0).
    :type phase: float
    :return: A generator yielding a function that takes frequency as input and
        returns the sniper scope signal function.
    :rtype: Generator[Callable[[float], Callable[[float], float]], None, None]
    """

    def update_scope(
        amplitude: float, phase: float = 0.0
    ) -> Callable[[float], Callable[[float], float]]:
        """
        Updates the frequency of the existing sniper scope signal.

        :param amplitude: The new amplitude of the sine wave.
        :type amplitude: float
        :param phase: The new phase shift of the sine wave in radians (default is 0).
        :type phase: float
        :return: A function that takes frequency as input and
            returns the updated sniper scope signal function.
        :rtype: Callable[[float], Callable[[float], float]]
        """

        return lambda frequency: generate_sine_function(
            frequency, amplitude, phase
        )

    try:
        yield update_scope(amplitude, phase)
    finally:
        pass  # Clean up resources if needed
