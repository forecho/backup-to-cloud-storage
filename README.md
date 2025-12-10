[![DigitalOcean Referral Badge](https://web-platforms.sfo2.digitaloceanspaces.com/WWW/Badge%203.svg)](https://www.digitalocean.com/?refcode=6087ccd0c9bb&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)

# Backup to Cloud Storage

Backup your database and files to Cloud Storage.

## What can it do?

- Backup MySQL database (local and Docker)
- Backup PostgreSQL database (local and Docker)
- Support multiple database instances (for multiple Docker projects)
- Backup directory (multiple)
- Upload to Aliyun OSS / Tencent COS / Backblaze B2

## How to use

### Install dependencies

```shell
sudo apt-get install zip -y
```

### Install python3

```shell
sudo apt-get install python3 python3-pip -y
pip3 install pyyaml
pip3 install oss2 # aliyun oss (optional)
pip3 install cos-python-sdk-v5 # tencent cos (optional)
pip3 install b2sdk # backblaze b2 (optional)
```

### Clone the project

```sh
git clone https://github.com/forecho/backup-to-cloud-storage.git
```

### Config

```sh
cd backup-to-cloud-storage && cp config.yaml.example config.yaml
```

Edit `config.yaml`:

```yaml
backup:
    driver: oss          # oss, cos, or b2
    name: myserver       # backup file prefix
    src: /var/www/html   # directories to backup (space separated)
    dir: /tmp/backup     # temp directory
    password: backup     # zip password

# Database configuration (all optional, supports multiple instances)
databases:
    mysql:
        # Local MySQL
        - name: local
          host: localhost
          user: root
          password: root
          databases: db1,db2

        # Docker MySQL (project A)
        - name: project_a
          container: project_a_mysql    # Docker container name
          user: root
          password: root
          databases: app_db

    postgres:
        # Docker PostgreSQL (project B)
        - name: project_b
          container: project_b_postgres
          user: postgres
          password: secret
          databases: app,analytics

# Cloud storage config (configure one)
oss:
    access_key_id: xxx
    access_key_secret: xxx
    endpoint: https://oss-cn-shenzhen.aliyuncs.com
    bucket: backup
```

#### Database Configuration

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Identifier for backup filename (e.g., `myserver-mysql-project_a-dbname.sql`) |
| `container` | No | Docker container name. If set, uses `docker exec` to backup |
| `host` | No | Database host (default: localhost, ignored when using container) |
| `port` | No | Database port (PostgreSQL only, default: 5432) |
| `user` | Yes | Database username |
| `password` | No | Database password |
| `databases` | Yes | Comma-separated database names |

#### How to get Docker container name

```sh
# List all running containers
docker ps

# Output example:
# CONTAINER ID   IMAGE          COMMAND                  NAMES
# a1b2c3d4e5f6   mysql:8.0      "docker-entrypoint.s…"   project_a_mysql
# f6e5d4c3b2a1   postgres:15    "docker-entrypoint.s…"   project_b_postgres
```

The `NAMES` column is the container name you need. If you use docker-compose, the container name is usually `{project_directory}_{service_name}_1` or `{project_name}-{service_name}-1`.

You can also find it in your `docker-compose.yml`:

```yaml
services:
  db:
    container_name: my_mysql    # <-- This is the container name
    image: mysql:8.0
```

If `container_name` is not set, use `docker ps` to check the actual name.

### Run

```sh
python3 backup.py
```

## Cron

```sh
crontab -e
```

Add this line to run backup at 2:00 AM daily:

```
0 2 * * * /usr/bin/python3 /root/backup-to-cloud-storage/backup.py
```

## Thanks

- [备份 vps 到七牛云存储脚本](https://github.com/ccbikai/backuptoqiniu)
- [阿里云 OSS 官方 SDK](https://github.com/aliyun/aliyun-oss-python-sdk)
