# DisCloud CDN
Python based cdn for posting your files. As this is a python project there are couple of limitations. Uploading files larger than 1gb are not recommended as the code is not optimized for big files. There also might be some bug in the code which have not been found.

## Local Setup
To run DisCloud instance on your local machine.

1. Install the code with `git clone https://github.com/Dishit79/Python-cdn.git`
2. Install all dependencies `pip install -r requirements.txt`
3. Create .env file like the one bellow:
```
CLIENT_ID="Discord client id" #If do not want to enable discord login, just put in a random string
CLIENT_SECRET="Discord client secret"
ADMIN_ACC_CODE="DISHIT" #The invite code which creates Admin accounts (never share this with anyone and reset after every use)
```
4. Run the script with `python main.py`




## Deployable Setup
To run DisCloud instance on a server for production use. (Follow same setup as Local Setup)


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
    server_name domain.xyz;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/cdn/Python-cdn/cdn.sock;
    }
}
```
### Full setup documentation [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)
