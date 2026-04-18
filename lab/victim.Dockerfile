FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx openssh-server rsyslog curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash labuser \
    && echo "labuser:labpass" | chpasswd \
    && mkdir -p /var/run/sshd /shared-logs/nginx

RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

RUN printf '%s\n' \
    'auth,authpriv.* /shared-logs/auth.log' \
    '& stop' \
    > /etc/rsyslog.d/20-0xchou00-auth.conf

RUN printf '%s\n' \
    'server {' \
    '    listen 80 default_server;' \
    '    listen [::]:80 default_server;' \
    '    server_name _;' \
    '    root /var/www/html;' \
    '    index index.html;' \
    '    access_log /shared-logs/nginx/access.log;' \
    '    error_log /var/log/nginx/error.log;' \
    '    location / {' \
    '        try_files $uri $uri/ =404;' \
    '    }' \
    '}' \
    > /etc/nginx/sites-available/default

RUN printf '%s\n' \
    '<html><body><h1>0xchou00 lab victim</h1></body></html>' \
    > /var/www/html/index.html

COPY lab/start-victim.sh /usr/local/bin/start-victim.sh
RUN chmod +x /usr/local/bin/start-victim.sh

EXPOSE 22 80

CMD ["/usr/local/bin/start-victim.sh"]
