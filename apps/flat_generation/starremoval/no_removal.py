
"""
Implementación del proceso de eliminación de estrellas que no modifica la imagen.

Devuelve el canal de imagen original sin cambios.
"""

from .base import StarRemovalProcess

class NoStarRemovalProcess(StarRemovalProcess):
    def apply(self, channel_image: 'numpy.ndarray', params: dict) -> 'numpy.ndarray':
        """
        Devuelve el canal de imagen original sin aplicar ningún procesamiento.

        Args:
            channel_image (numpy.ndarray): Canal de imagen de entrada.
            params (dict): Parámetros (no utilizados en este método).

        Returns:
            numpy.ndarray: Canal de imagen sin modificar.
        """
        return channel_image