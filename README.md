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

You'll also need to add your own `NYT_BOOKS_API_KEY` to `.env`.

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

To list every resource on the stack, run the following command:
```
aws cloudformation describe-stack-resources --stack-name read-track-capstone
```


### Delete the stack

Run this command from the project root on your local machine:
```
aws cloudformation delete-stack --stack-name read-track-capstone --region <REGION_NAME>
```
Please note that the policy does not delete the S3 bucket created by the template. This prevents the deletion from failing if the S3 bucket has any files in it. When you're done with the project, you will need to delete it manually.

### Applying migrations to the deployed database

RDS isn't reachable directly. Connect through the EC2 instance instead:

```bash
aws ssm start-session --target <EC2InstanceId from stack outputs>
```

From inside that session, fetch the DB password and run migrations:
```bash
aws secretsmanager get-secret-value --secret-id <DBSecretArn from stack outputs> \
  --query SecretString --output text
# then export DATABASE_URL using that password + the DBEndpointAddress output
export FLASK_APP=app.app
flask db upgrade
```