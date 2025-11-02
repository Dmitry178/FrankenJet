FROM docker.elastic.co/elasticsearch/elasticsearch:9.2.0

RUN elasticsearch-plugin install --batch analysis-icu

USER root
RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/plugins
USER elasticsearch
