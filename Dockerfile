FROM mambaorg/micromamba:1.5.5

# Pfad für Micromamba
ENV MAMBA_DOCKERFILE_ACTIVATE=1

# Kopiere environment.yml
COPY environment.yml /tmp/environment.yml

# Erstelle Conda-Environment
RUN micromamba create -f /tmp/environment.yml -y && \
    micromamba clean --all --yes

# Setze das Environment als standardmäßig aktiv
SHELL ["micromamba", "run", "-n", "combined-env", "/bin/bash", "-c"]

# Installiere den Kernel
RUN python -m ipykernel install --user --name combined-env --display-name "Renku Combined Env"

# Arbeitsverzeichnis
WORKDIR /home/renku/work