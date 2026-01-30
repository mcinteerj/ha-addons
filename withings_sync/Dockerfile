ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install Python, jq, and withings-sync
RUN apk add --no-cache python3 py3-pip jq
RUN pip3 install --no-cache-dir --break-system-packages withings-sync

# Copy run script
COPY run.sh /
RUN chmod +x /run.sh

CMD ["/run.sh"]
