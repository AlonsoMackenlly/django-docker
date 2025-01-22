# syntax=docker/dockerfile:1
# Сборочный этап.
# В качестве базового образа используем Ubuntu, так как в основном разработка у нас ведётся на этой ОС.
# При этом ничто не мешает использовать официальные образы Python от Docker.
FROM ubuntu:noble AS build

ARG python_version=3.12

# Переопределяем стандартную команду запуска шелла для выполнения команд в форме "shell".
# https://docs.docker.com/reference/dockerfile/#shell-and-exec-form
# Опция `-e` включает мгновенный выход после ошибки для любой непроверенной команды.
#   Команда считается проверенной, если она используется в условии оператора ветвления (например, `if`)
#   или является левым операндом `&&` либо `||` оператора.
# Опция `-x` включает печать каждой команды в поток stderr перед её выполнением. Она очень полезна при отладке.
# https://manpages.ubuntu.com/manpages/noble/en/man1/sh.1.html
#SHELL ["/bin/sh", "-exc"]

# Устанавливаем системные пакеты для сборки проекта.
# Используем команду `apt-get`, а не `apt`, так как у последней нестабильный интерфейс.
# `libpq-dev` — это зависимость `psycopg2` — пакета Python для работы с БД, который будет компилироваться при установке.
RUN <<EOF
apt-get update --quiet
apt-get install --quiet --no-install-recommends --assume-yes \
  build-essential \
  libpq-dev \
  "python$python_version-dev"
EOF

# Копируем утилиту `uv` из официального Docker-образа.
# https://github.com/astral-sh/uv/pkgs/container/uv
# опция `--link` позволяет переиспользовать слой, даже если предыдущие слои изменились.
# https://docs.docker.com/reference/dockerfile/#copy---link
COPY --link --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv

# Задаём переменные окружения.
# UV_PYTHON — фиксирует версию Python.
# UV_PYTHON_DOWNLOADS — отключает автоматическую загрузку отсутствующих версий Python.
# UV_PROJECT_ENVIRONMENT — указывает путь к виртуальному окружению Python.
# UV_LINK_MODE — меняет способ установки пакетов из глобального кэша.
#   Вместо создания жёстких ссылок, файлы пакета копируются в директорию  виртуального окружения `site-packages`.
#   Это необходимо для будущего копирования изолированной `/home/user` директории из  стадии `build` в финальный Docker-образ.
# UV_COMPILE_BYTECODE — включает компиляцию файлов Python в байт-код после установки.
# https://docs.astral.sh/uv/configuration/environment/
# PYTHONOPTIMIZE — убирает инструкции `assert` и код, зависящий от значения  константы `__debug__`,
#   при компиляции файлов Python в байт-код.
# https://docs.python.org/3/using/cmdline.html#environment-variables
ENV UV_PYTHON="python$python_version" \
  UV_PYTHON_DOWNLOADS=never \
  UV_PROJECT_ENVIRONMENT=/venv \
  UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  PYTHONOPTIMIZE=1

# Копируем файлы, необходимые для установки зависимостей без кода проекта, так как обычно зависимости меняются реже кода.
COPY pyproject.toml uv.lock /app/

# Для быстрой локальной установки зависимостей монтируем кэш-директорию, в которой будет храниться глобальный кэш uv.
# Первый вызов `uv sync` создаёт виртуальное окружение и устанавливает зависимости без текущего проекта.
# Опция `--frozen` запрещает обновлять `uv.lock` файл.
RUN --mount=type=cache,destination=/root/.cache/uv <<EOF
cd /app
uv sync \
  --frozen
EOF

# Переключаемся на интерпретатор из виртуального окружения.
ENV UV_PYTHON=$UV_PROJECT_ENVIRONMENT

COPY VERSION /app/
COPY README.md /app/
COPY backend/ /app/

# Финальный этап.
FROM ubuntu:noble AS final

WORKDIR /app

# Два следующих аргумента позволяют изменить UID и GID пользователя Docker-контейнера.
ARG PUID=1000
ARG PGID=1000
ARG python_version=3.12
# Устанавливаем системные пакеты для запуска проекта.
# Обратите внимание, что в именах пакетов нет суффиксов "dev".
RUN <<EOF
apt-get update --quiet
apt-get install --quiet --no-install-recommends --assume-yes \
  libpq5 \
  "python$python_version" \
  openssh-server \
  sudo
rm -rf /var/lib/apt/lists/*
EOF


ENTRYPOINT ["/docker-entrypoint.sh"]
# Для приложений на Python лучше использовать сигнал SIGINT, так как не все фреймворки (например, gRPC) корректно обрабатывают сигнал SIGTERM.
STOPSIGNAL SIGINT
EXPOSE 8080/tcp

# Создаём группу и пользователя с нужными ID.
# Если значение ID больше нуля (исключаем "root" ID) и в системе уже есть пользователь или группа с указанным ID,
# пересоздаём пользователя или группу с именем "venv".
RUN <<EOF
[ $PUID -gt 0 ] && user="$(id --name --user $PUID 2> /dev/null)" && userdel "$user"

if [ $PGID -gt 0 ]; then
  group="$(id --name --group $PGID 2> /dev/null)" && groupdel "$group"
  groupadd --gid $PGID user
fi

[ $PUID -gt 0 ] && useradd --uid $PUID --gid $PGID --home-dir /home/user user
EOF

RUN mkdir /home/user
RUN adduser user sudo

RUN echo "export PATH=/venv/bin:$PATH" >> /home/user/.bashrc && \
    chown -R user:user /home/user

# Задаём переменные окружения.
# PATH — добавляет директорию виртуального окружения `bin` в начало списка директорий с исполняемыми файлами.
#   Это позволяет запускать Python-утилиты из любой директории контейнера без указания полного пути к файлу.
# PYTHONOPTIMIZE — указывает интерпретатору Python, что нужно использовать ранее скомпилированные файлы из  директории `__pycache__` с  суффиксом `opt-1` в имени.
# PYTHONFAULTHANDLER — устанавливает обработчики ошибок для дополнительных сигналов.
# PYTHONUNBUFFERED — отключает буферизацию для потоков stdout и stderr.
# https://docs.python.org/3/using/cmdline.html#environment-variables

COPY docker/django/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENV PATH=/venv/bin:$PATH \
  PYTHONOPTIMIZE=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1

################ <SSH> ################
# Создаем директорию для SSH ключей и устанавливаем права
RUN mkdir /home/user/.ssh && \
    chmod 700 /home/user/.ssh


COPY docker/ssh/id_rsa.pub /home/user/.ssh/authorized_keys

# Устанавливаем права на файл authorized_keys
RUN chmod 600 /home/user/.ssh/authorized_keys

# Configure the SSH server
RUN mkdir /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#AuthorizedKeysFile/AuthorizedKeysFile/' /etc/ssh/sshd_config && \
    sed -i 's/#HostKey \/etc\/ssh\/ssh_host_rsa_key/HostKey ~\/.ssh\/ssh_host_rsa_key/' /etc/ssh/sshd_config && \
    sed -i 's/#HostKey \/etc\/ssh\/ssh_host_ecdsa_key/HostKey ~\/.ssh\/ssh_host_ecdsa_key/' /etc/ssh/sshd_config && \
    sed -i 's/#HostKey \/etc\/ssh\/ssh_host_ed25519_key/HostKey ~\/.ssh\/ssh_host_ed25519_key/' /etc/ssh/sshd_config && \
    cp /etc/ssh/sshd_config /home/user/.ssh/sshd_config

RUN chown -R user:user /home/user

RUN ssh-keygen -A

USER $PUID:$PGID

RUN ssh-keygen -A

RUN <<EOF
ssh-keygen -t rsa -f /home/user/.ssh/id_rsa -P ''
ssh-keygen -q -N "" -t dsa -f /home/user/.ssh/ssh_host_dsa_key
ssh-keygen -q -N "" -t rsa -b 4096 -f /home/user/.ssh/ssh_host_rsa_key
ssh-keygen -q -N "" -t ecdsa -f /home/user/.ssh/ssh_host_ecdsa_key
ssh-keygen -q -N "" -t ed25519 -f /home/user/.ssh/ssh_host_ed25519_key
EOF
################ </SSH> ################

# Копируем директорию с виртуальным окружением из предыдущего этапа.
COPY --link --chown=$PUID:$PGID --from=build /venv/ /venv
COPY --chown=$PUID:$PGID --from=build /app/ /app/

EXPOSE 22

# Start the program
CMD ["python", "-V"]

FROM final AS debug

# Start the SSH server
CMD ["/usr/sbin/sshd", "-D"]
