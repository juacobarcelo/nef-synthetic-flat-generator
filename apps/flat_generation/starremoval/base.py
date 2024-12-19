
"""
Definición de la clase base para los procesos de eliminación de estrellas.

Proporciona la interfaz que deben implementar todas las clases derivadas.
"""

class StarRemovalProcess:
    def apply(self, channel_image: 'numpy.ndarray', params: dict) -> 'numpy.ndarray':
        """
        Aplica el proceso de eliminación de estrellas y suavizado al canal de imagen dado.

        Args:
            channel_image (numpy.ndarray): Canal de imagen de entrada.
            params (dict): Parámetros para el método de eliminación de estrellas.

        Returns:
            numpy.ndarray: Canal de imagen procesado.
        """
        raise NotImplementedError("Este método debe ser implementado por la subclase.")