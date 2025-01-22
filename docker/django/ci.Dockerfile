# syntax=docker/dockerfile:1

ARG DJANGO_IMAGE=$DJANGO_IMAGE

FROM $DJANGO_IMAGE

RUN <<EOF
apt-get update --quiet
apt install --quiet --no-install-recommends --assume-yes \
  git \
  ca-certificates

git config --global --add safe.directory '*'
EOF

RUN <<EOF
uv tool run --compile-bytecode pre-commit --version
EOF

COPY .pre-commit-config.yaml /app/

RUN <<EOF
cd /app
git init
uv tool run pre-commit install-hooks
uv tool run pre-commit run --all-files
EOF

