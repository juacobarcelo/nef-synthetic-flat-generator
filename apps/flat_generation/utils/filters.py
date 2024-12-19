
"""
Implementación de filtros y funciones de procesamiento de imágenes.

Incluye filtros de mediana y suavizado Gaussiano.
"""

import numpy as np
from scipy.ndimage import median_filter, gaussian_filter

def apply_median_filter(image: 'numpy.ndarray', size: int) -> 'numpy.ndarray':
    """
    Aplica un filtro de mediana a la imagen.

    Args:
        image (numpy.ndarray): Imagen de entrada.
        size (int): Tamaño del filtro de mediana.

    Returns:
        numpy.ndarray: Imagen filtrada.
    """
    # ...código por implementar...

def apply_gaussian_blur(image: 'numpy.ndarray', sigma: float) -> 'numpy.ndarray':
    """
    Aplica un suavizado Gaussiano a la imagen.

    Args:
        image (numpy.ndarray): Imagen de entrada.
        sigma (float): Desviación estándar para el filtro Gaussiano.

    Returns:
        numpy.ndarray: Imagen suavizada.
    """
    # ...código por implementar...