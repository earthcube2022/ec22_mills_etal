FROM conda/miniconda3

RUN apt-get update
RUN apt-get install -y nano gcc
RUN pip install notebook
WORKDIR /books
COPY environment.yml /books/environment.yml
SHELL ["/bin/bash", "-c"]
RUN conda env create -f environment.yml && conda init bash && source ~/.bashrc && conda activate py_NSF_EC2022 && conda install -y -c anaconda ipykernel && python -m ipykernel install --user --name=py_NSF_EC2022 && conda deactivate
CMD jupyter notebook --allow-root --ip=0.0.0.0
