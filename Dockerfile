# Use Kali Linux as the base image
FROM kalilinux/kali-rolling

# Define grouped package variables
ARG APP_DEPENDENCIES="aircrack-ng cowpatty kmod"
ARG PYTHON_ENV="python3 python3-pip"
ARG SYSTEM_TOOLS="procps pciutils"

# Install dependencies using grouped variables
RUN apt update && apt install -y --no-install-recommends \
    ${APP_DEPENDENCIES} \
    ${PYTHON_ENV} \
    ${SYSTEM_TOOLS} \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Install APP Python dependencies
RUN pip install --no-cache-dir psutil --break-system-packages
RUN pip install --no-cache-dir rich --break-system-packages
RUN pip install --no-cache-dir simple-term-menu --break-system-packages

# Suppress the login message by creating ~/.hushlogin
RUN touch /root/.hushlogin

# Create alias for python3 → python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set the working directory
WORKDIR /opt/airsmack

# Set entrypoint to keep the container running
CMD ["/bin/bash"]