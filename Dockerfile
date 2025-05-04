FROM oraclelinux:8

# Установить зависимости для сборки RPM и запуска Python
RUN dnf -y install python3 rpm-build shadow-utils

# Создать пользователя для сборки
RUN useradd user
USER user
WORKDIR /home/user

# Создать структуру каталогов для rpmbuild
RUN mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Скопировать исходники и spec-файл
COPY chat/ rpmbuild/SOURCES/chat/
COPY tcp-chat.spec rpmbuild/SPECS/tcp-chat.spec

# Войти как root для установки RPM
USER root

# Сделать файлы запуска исполняемыми
RUN chmod +x rpmbuild/SOURCES/chat/startup/tcp-server rpmbuild/SOURCES/chat/startup/tcp-client

# Собрать RPM
RUN rpmbuild --define "_topdir /home/user/rpmbuild" -bb rpmbuild/SPECS/tcp-chat.spec

# Установить собранный RPM
RUN dnf -y install /home/user/rpmbuild/RPMS/noarch/tcp-chat-*.rpm