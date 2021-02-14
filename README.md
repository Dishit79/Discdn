# DisCloud CDN

## Setup

### Systemd Service

```
[Unit]
Description=Gunicorn instance to serve DisCloud's website
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/cdn/Python-cdn
Environment="PATH=/var/www/cdn/Python-cdn/env/bin"
ExecStart=/var/www/cdn/Python-cdn/env/bin/gunicorn --workers 3 --bind unix:cdn.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

### NGINX

```
server {
    listen 80;
    server_name domain.xyz www.domain.xyz;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/cdn/Python-cdn/cdn.sock;
    }
}
```
### Full documentation [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04#step-4-%E2%80%94-configuring-gunicorn)
