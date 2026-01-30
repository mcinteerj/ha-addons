ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install Python and withings-sync
RUN apk add --no-cache python3 py3-pip py3-lxml
RUN pip3 install --no-cache-dir --break-system-packages withings-sync

# Copy run script
COPY run.sh /
RUN chmod +x /run.sh

CMD ["/run.sh"]
