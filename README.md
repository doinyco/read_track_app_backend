# read_track_app_backend
Backend API for Read Track, a reading-habit tracker built with Flask and PostgreSQL

-----

## Database Setup (Local Development)

This project uses PostgreSQL, run locally via Docker, with SQLAlchemy + Flask-Migrate for schema management.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Python dependencies installed: `pip install -r requirements.txt`

### 1. Set up environment variables

Copy the example env file and fill in real values:

```bash
cp .env.example .env
```

The default `DATABASE_URL` in `.env.example` already matches the port and credentials configured in `docker-compose.yml` — you shouldn't need to change it.

You'll also need to fill in `POSTGRES_PASSWORD`, `SECRET_KEY`, `GOOGLE_BOOKS_API_KEY`, and `NYT_BOOKS_API_KEY`.

### 2. Start Postgres

```bash
docker compose up -d
```

Confirm it's healthy:

```bash
docker compose ps
```

You should see `bookapp-local-db` with status `Up (healthy)`.

### 3. Apply migrations

```bash
export FLASK_APP=app.app
flask db upgrade
```

This creates all tables (`books`, `users`, `reading_lists`, `progress`) based on the existing migration history in `migrations/`. You should **not** need to run `flask db init` or `flask db migrate` — those are one-time/schema-change commands already reflected in this repo.

### 4. Verify

```bash
docker exec -it bookapp-local-db psql -U postgres -d bookapp -c "\dt"
```

You should see all four tables plus `alembic_version`.

Then run the app:

```bash
flask run
```

### Troubleshooting

- **`FATAL: database "bookapp" does not exist`** — the Docker container's data volume may be stale or corrupted. Reset it and start fresh:
```bash
  docker compose down -v
  docker compose up -d
  flask db upgrade
```
- **Migration errors after pulling new changes** — someone may have added a new migration file. Just re-run `flask db upgrade` to apply anything new.

-----

## AWS CloudFormation stack deployment

### Deploy the stack

Run this command from the project root on your local machine:
```
aws cloudformation deploy \
  --template-file infra/cloudformation-stack.yaml \
  --stack-name read-track-capstone \
  --region <REGION_NAME> \
  --parameter-overrides OwnerTag="<YOUR_NAME>" \
  --capabilities CAPABILITY_NAMED_IAM
```
Please note that `<REGION_NAME>` and `<YOUR_NAME>` need to be replaced with the AWS region you want to deploy to and your own name, respectively.

### Check your stack

To see a collection of useful outputs (DB endpoint, bucket name, EC2 IP, etc.), run the following command on the project root:
```
aws cloudformation describe-stacks --stack-name read-track-capstone \
  --query "Stacks[0].Outputs" --output table
```

(Omit `--output table` if you want to return the output as an array of dictionaries instead.)

To list every resource on the stack, run the following command:
```
aws cloudformation describe-stack-resources --stack-name read-track-capstone
```


### Delete the stack

Run this command from the project root on your local machine:
```
aws cloudformation delete-stack --stack-name read-track-capstone --region <REGION_NAME>
```

The S3 bucket is intentionally excluded from stack deletion (`DeletionPolicy: Retain`) — cover images are cheap to keep, and CloudFormation can't delete a non-empty bucket anyway. To remove it too:
```bash
aws s3 rm s3://<bucket-name> --recursive
aws s3api delete-bucket --bucket <bucket-name>
```
**If you plan to redeploy afterward, delete the bucket first.** `BucketName` is a fixed, deterministic value — CloudFormation will fail to create a new stack while an orphaned bucket with that same name still exists.

### Deploy the Flask app to EC2 and connect the local frontend

Do this after the CloudFormation stack is deployed (see "Check your stack" above for how to get the outputs you'll need below).

#### 1. Connect to the instance
```bash
aws ssm start-session --target <EC2InstanceId>
```
SSM connects you as `ssm-user`, not `ec2-user` — switch right away, since the systemd service below runs as `ec2-user`:
```bash
sudo -iu ec2-user
```

#### 2. Clone the repo and install dependencies
```bash
sudo dnf install -y python3.11 git
git clone https://github.com/doinyco/read_track_app_backend.git
cd read_track_app_backend

# AL2023's default python3 is 3.9, too old for this project's pinned
# Alembic version (requires 3.10+) -- use python3.11 for the venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
Private repo? Use a personal access token in the URL instead: `https://<username>:<token>@github.com/...`

#### 3. Build the `.env` file
Pull `DBSecretArn`, `DBEndpointAddress`, and `S3BucketName` from the stack outputs first.
```bash
DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id '<DBSecretArn>' \
  --query SecretString --output text | python3 -c "import json,sys; print(json.load(sys.stdin)['password'])")

cat > .env << EOF
DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@<DBEndpointAddress>:5432/bookapp
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FRONTEND_URL=http://localhost:5173
GOOGLE_BOOKS_API_KEY=<your key>
NYT_BOOKS_API_KEY=<your key>
S3_BUCKET_NAME=<S3BucketName output>
AWS_REGION=<your region>
EOF
```
Single-quote the `--secret-id` value — RDS-managed secret names contain a literal `!`, which bash otherwise reads as history expansion.

#### 4. Run migrations
```bash
export FLASK_APP=app.app
flask db upgrade
```

#### 5. Run the app as a systemd service
```bash
sudo tee /etc/systemd/system/readtrack.service > /dev/null << EOF
[Unit]
Description=Read Track Flask app
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$(pwd)
EnvironmentFile=$(pwd)/.env
ExecStart=$(pwd)/venv/bin/gunicorn --bind 0.0.0.0:5000 app.app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now readtrack
sudo systemctl status readtrack
```
Look for `active (running)`. If `failed`, check `sudo journalctl -u readtrack -n 50 --no-pager`.

#### 6. Point the local frontend at it
In the **frontend** repo, create `.env.local` (gitignored — every teammate sets their own):

VITE_API_URL=/api
VITE_EC2_URL=http://<EC2PublicIp>:5000/

Then:
```bash
npm run dev
```
Open `http://localhost:5173` and confirm end-to-end — register a user, search for a book. The frontend talks to `/api/*` on `localhost`, and Vite's dev server proxies that to EC2 server-side — this keeps the browser's view of everything as same-origin, which avoids a cross-site cookie restriction that would otherwise silently break login (the backend runs on plain HTTP with no domain, so cookies can't use the `SameSite=None; Secure` that a genuine cross-site request would require).

#### Troubleshooting
- **Not reachable at all** — confirm `systemctl status readtrack` shows `active (running)`, and that you're using the *current* `EC2PublicIp` (it changes if the stack is ever torn down and recreated).
- **401 on every request despite a successful login** — usually means the frontend is bypassing the proxy. Check `VITE_API_URL=/api`, not the full EC2 URL.
- **Book covers not showing up in S3** — check `sudo journalctl -u readtrack -n 50 --no-pager | grep "S3 upload failed"` on EC2.