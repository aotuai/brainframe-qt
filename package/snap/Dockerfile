################################################################################
# Build
################################################################################

FROM cibuilds/snapcraft:core18 AS snap-build

RUN sudo rm -rf /snap/snapcraft/current

# Manually install the snapcraft snap 4.x, latest stable is not compatible
RUN curl -L $(curl -H "X-Ubuntu-Series: 16" "https://api.snapcraft.io/api/v1/snaps/details/snapcraft?channel=4.x/stable" | jq ".download_url" -r) --output snapcraft.snap && \
	sudo mkdir -p /snap/snapcraft && \
	sudo unsquashfs -d /snap/snapcraft/current snapcraft.snap && \
	rm -f snapcraft.snap

RUN sudo apt-get update && \
    sudo apt-get -y --no-install-recommends install \
        # For Poetry
        python3-dev curl git \
        # For Qt
        qt5-default qttools5-dev-tools qttools5-dev-tools \
        # For Gstly/PyGObject
        python3-gi python3-gst-1.0 libgirepository1.0-dev libcairo2-dev gir1.2-gstreamer-1.0 && \
    sudo rm -rf /var/lib/apt/lists/*

# Install Poetry
ARG POETRY_VERSION=1.1.4
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py \
    | python3 - --version $POETRY_VERSION
ENV PATH="${PATH}:~/.poetry/bin"

# Create a workdir
RUN sudo install -d -o circleci -g circleci /brainframe-qt
WORKDIR /brainframe-qt

# Install dependencies
COPY --chown=circleci pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root -E build -E resource_build

# Add project source
COPY --chown=circleci . .

# Build Resources
RUN poetry run python3 scripts/compile_qt_resources.py

# Build snap
RUN mkdir ./snap/ && cp -r package/snap/snap/ .

RUN snapcraft

################################################################################
# Output
################################################################################

FROM scratch AS output

WORKDIR /output
COPY --from=snap-build /brainframe-qt/brainframe-client_*.snap .

ENTRYPOINT bash
