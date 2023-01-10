# We'll start from a prebaked debian miniconda container
ARG CI_REGISTRY
FROM ${CI_REGISTRY}/innersource/docker/miniconda:debian
WORKDIR /

SHELL ["/bin/bash", "--login", "-c"]

RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> /root/.bashrc
RUN /opt/conda/condabin/conda init bash
RUN /opt/conda/condabin/conda config --add channels conda-forge
ADD gd2-conda-environment.yml /root/gd2-conda-environment.yml
RUN /opt/conda/condabin/conda env create -f /root/gd2-conda-environment.yml
RUN echo "conda activate gd2" >> /root/.bashrc

# Finally, when we're done with our image let's go ahead and clean up all our
# intermediate work that doesn't need to hang around. This will make our
# docker image a bit smaller.
RUN rm -rf /tmp/* /var/tmp/*

SHELL ["/bin/bash", "--login", "-c"]
CMD ["/bin/bash", "-l"]

