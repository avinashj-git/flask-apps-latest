Here's a complete, copy-paste friendly guide with all commands and a README.md template for your Flask deployment project:

📝 README.md (Copy-Paste Template)
markdown
# Flask Docker Deployment on AWS EC2

Automated CI/CD pipeline for Flask app using Docker, GitHub Actions, and AWS EC2.

## 🌟 Features
- Dockerized Flask app
- GitHub Actions CI/CD
- DockerHub webhook auto-deployment
- Production-ready Gunicorn setup

## 🛠️ Prerequisites
- AWS EC2 (Amazon Linux 2023)
- DockerHub account
- GitHub repository

## 🔧 Setup Steps

### 1. EC2 Configuration
```bash
# On BOTH Dev and Prod EC2:
sudo yum update -y
sudo yum install -y docker git python3
sudo systemctl start docker
sudo systemctl enable docker
2. Flask App Setup
bash
mkdir flask-app && cd flask-app
cat > app.py <<EOL
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Flask!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
EOL

cat > Dockerfile <<EOL
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install flask gunicorn
EXPOSE 6000
CMD ["gunicorn", "--bind", "0.0.0.0:6000", "app:app"]
EOL
3. GitHub Actions CI/CD
Create .github/workflows/docker.yml:

yaml
name: Build and Push
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: \${{ secrets.DOCKERHUB_USERNAME }}
          password: \${{ secrets.DOCKERHUB_TOKEN }}
      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: \${{ secrets.DOCKERHUB_USERNAME }}/flask-app:latest
4. Production EC2 Setup
bash
# Webhook listener setup
sudo mkdir -p /opt/webhooks
cat > /opt/webhooks/dockerhub-listener.py <<EOL
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/dockerhub-webhook', methods=['POST'])
def webhook():
    if request.headers.get('Content-Type') == 'application/json':
        subprocess.run(["/opt/update-flask.sh"], shell=True)
        return "Deployment triggered!", 200
    return "Invalid content", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
EOL

# Update script
cat > /opt/update-flask.sh <<EOL
#!/bin/bash
docker stop flask-app || true
docker rm flask-app || true
docker rmi your-dockerhub-username/flask-app:latest || true
docker pull your-dockerhub-username/flask-app:latest
docker run -d -p 5000:6000 --name flask-app your-dockerhub-username/flask-app:latest
echo "\$(date) - Updated container" >> /var/log/webhook-updates.log
EOL

chmod +x /opt/update-flask.sh

# Systemd service
cat > /etc/systemd/system/webhook-listener.service <<EOL
[Unit]
Description=DockerHub Webhook Listener
After=network.target

[Service]
User=root
WorkingDirectory=/opt/webhooks
ExecStart=/usr/bin/python3 /opt/webhooks/dockerhub-listener.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl start webhook-listener
sudo systemctl enable webhook-listener
🔍 Verification
bash
# Check running containers
docker ps

# Test endpoint
curl http://localhost:5000

# Check logs
journalctl -u webhook-listener -f
🚀 Deployment Workflow
Push code → GitHub Actions builds image → DockerHub

DockerHub webhook → EC2 listener → Runs update script

New container starts automatically

📜 License
MIT

text

---

### **🔗 Key Files Summary**

#### **1. `update-flask.sh` (Production EC2)**
```bash
#!/bin/bash
# Force clean update
docker stop flask-app || true
docker rm flask-app || true
docker rmi your-dockerhub-username/flask-app:latest || true

# Pull and run with correct port mapping
docker pull your-dockerhub-username/flask-app:latest
docker run -d -p 5000:6000 --name flask-app your-dockerhub-username/flask-app:latest

# Logging
echo "$(date) - Container updated" >> /var/log/webhook-updates.log
docker ps >> /var/log/webhook-updates.log
2. dockerhub-listener.py (Webhook Endpoint)
python
from flask import Flask, request
import subprocess
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/dockerhub-webhook', methods=['POST'])
def webhook():
    if request.headers.get('Content-Type') == 'application/json':
        logging.info("Webhook received, triggering update...")
        result = subprocess.run(
            ["/bin/bash", "/opt/update-flask.sh"],
            capture_output=True,
            text=True
        )
        logging.info(f"Script output:\n{result.stdout}")
        if result.stderr:
            logging.error(f"Script errors:\n{result.stderr}")
        return "Deployment started", 200
    return "Invalid content", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
✅ Post-Setup Checklist
Added DOCKERHUB_USERNAME and DOCKERHUB_TOKEN to GitHub Secrets

Created DockerHub webhook pointing to http://<EC2_IP>:5001/dockerhub-webhook

Opened EC2 security group ports:

5000 (Flask app)

5001 (webhook listener)

22 (SSH)

Tested manual deployment with:

bash
/opt/update-flask.sh
curl http://localhost:5000
📌 Pro Tips
For debugging:

bash
# Container logs
docker logs -f flask-app

# Webhook listener logs
journalctl -u webhook-listener -f
To clean up old images:

bash
docker system prune -a -f
For HTTPS (future upgrade):

bash
sudo yum install nginx certbot python3-certbot-nginx
