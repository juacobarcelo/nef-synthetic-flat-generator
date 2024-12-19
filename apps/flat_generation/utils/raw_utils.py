
"""
Funciones utilitarias para extraer y manipular datos RAW de archivos NEF.

Incluye funciones para leer los datos sin demosaicing y extraer canales Bayer.
"""

def read_raw_data(nef_file: str) -> 'numpy.ndarray':
    """
    Lee los datos RAW de un archivo NEF sin aplicar demosaicing.

    Args:
        nef_file (str): Ruta al archivo NEF.

    Returns:
        numpy.ndarray: Datos RAW del archivo.
    """
    # ...código por implementar...

def extract_bayer_channels(raw_data: 'numpy.ndarray', pattern: str) -> dict:
    """
    Extrae los canales individuales del patrón Bayer.

    Args:
        raw_data (numpy.ndarray): Datos RAW del archivo NEF.
        pattern (str): Patrón Bayer (e.g., 'RGGB').

    Returns:
        dict: Diccionario con los canales 'R', 'G', 'B' extraídos.
    """
    # ...código por implementar...