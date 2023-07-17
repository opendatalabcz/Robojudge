# To get the fresh environment.yml file: conda lock -p linux-64 -f server/environment.yml

FROM python:3.10-slim as BUILD_STAGE

# Install base utilities
RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH
ENV CONDA_ENV_NAME="bp-server"

RUN apt update
RUN apt install g++ -y

# TODO: Clean up unused shit
COPY environment.yml .

RUN conda create -n $CONDA_ENV_NAME python=3.10
RUN conda env update -n $CONDA_ENV_NAME --file environment.yml

# https://stackoverflow.com/questions/55123637/activate-conda-environment-in-docker
# Make RUN commands use the new environment:
SHELL ["conda", "run", "--no-capture-output", "-n", "$CONDA_ENV_NAME", "/bin/bash", "-c"]

# RUN echo "source activate CONDA_ENV_NAME" > ~/.bashrc
# RUN conda init bash
# RUN conda activate CONDA_ENV_NAME

COPY . .

# Install the server directory as a pip module to make imports work
RUN pip install -e .

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "$CONDA_ENV_NAME", "python3", "server/main.py"]