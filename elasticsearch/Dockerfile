FROM elasticsearch:8.19.2

RUN elasticsearch-plugin install --batch analysis-icu

USER root
RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/plugins
USER elasticsearch
