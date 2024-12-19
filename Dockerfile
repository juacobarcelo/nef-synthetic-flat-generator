
FROM python:3.9-buster

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    exiftool \
    libexiv2-dev \
    libopenexr-dev \
    libfftw3-dev \
    libraw-dev \
    libtiff5-dev \
    libboost-all-dev \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar StarNet++
RUN mkdir /opt/starnet && \
    cd /opt/starnet && \
    wget https://starnetastro.com/wp-content/uploads/2022/03/StarNetv2CLI_linux.zip && \
    unzip StarNetv2CLI_linux.zip && \
    chmod +x ./starnet++ && \
    ln -s /opt/starnet/starnet++ /usr/local/bin/starnet++


# Establecer el directorio de trabajo
WORKDIR /apps

# Copiar los archivos del proyecto al contenedor
COPY apps /apps

# Instalar las dependencias de Python
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Comando por defecto
CMD ["/bin/bash"]