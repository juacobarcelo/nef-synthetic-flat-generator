
"""
Implementación del proceso de eliminación de estrellas utilizando filtro de mediana.

Detecta y elimina estrellas aplicando un umbral y filtrado de mediana.
"""

from .base import StarRemovalProcess
import numpy as np
from scipy.ndimage import median_filter

class MedianFilterStarRemoval(StarRemovalProcess):
    def apply(self, channel_image: 'numpy.ndarray', params: dict) -> 'numpy.ndarray':
        """
        Aplica eliminación de estrellas mediante filtrado de mediana.

        Args:
            channel_image (numpy.ndarray): Canal de imagen de entrada.
            params (dict): Parámetros para el filtrado.
                - 'threshold' (float): Umbral para detección de estrellas.
                - 'median_filter_size' (int): Tamaño del filtro de mediana.

        Returns:
            numpy.ndarray: Canal de imagen procesado.
        """
        # ...código por implementar...