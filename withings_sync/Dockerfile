ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install Python, pip, jq, and dependencies
RUN apk add --no-cache python3 py3-pip py3-flask jq

# Install withings-sync
RUN pip3 install --no-cache-dir --break-system-packages withings-sync requests

# Copy application files
COPY server.py /
COPY templates /templates
COPY run.sh /
RUN chmod +x /run.sh

# Expose ingress port
EXPOSE 8099

CMD ["/run.sh"]
