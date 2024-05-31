FROM runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04
WORKDIR /content
ENV PATH="/home/camenduru/.local/bin:${PATH}"
RUN adduser --disabled-password --gecos '' camenduru && \
    adduser camenduru sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    chown -R camenduru:camenduru /content && \
    chmod -R 777 /content && \
    chown -R camenduru:camenduru /home && \
    chmod -R 777 /home

RUN apt update -y && add-apt-repository -y ppa:git-core/ppa && apt update -y && apt install -y aria2 git git-lfs unzip ffmpeg

USER camenduru

RUN pip install -q opencv-python imageio imageio-ffmpeg ffmpeg-python av runpod \
    xformers==0.0.25 decord==0.6.0 einops==0.3.0 numpy==1.24.2 omegaconf==2.1.1 opencv_python pandas==2.0.0 Pillow==9.5.0 pytorch_lightning==1.9.3 PyYAML==6.0 \
    setuptools==65.6.3 tqdm==4.65.0 transformers==4.25.1 moviepy timm scikit-learn open_clip_torch==2.22.0 kornia diffusers

RUN git clone -b dev https://github.com/camenduru/ToonCrafter /content/ToonCrafter

RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/Doubiiu/ToonCrafter/resolve/main/model.ckpt -d /content/ToonCrafter/checkpoints/tooncrafter_512_interp_v1 -o model.ckpt

COPY ./worker_runpod.py /content/ToonCrafter/worker_runpod.py
WORKDIR /content/ToonCrafter
CMD python worker_runpod.py