[![DigitalOcean Referral Badge](https://web-platforms.sfo2.digitaloceanspaces.com/WWW/Badge%203.svg)](https://www.digitalocean.com/?refcode=6087ccd0c9bb&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)

# 备份到云存储

将您的数据库和文件备份到云存储。

## 功能特性

- 备份 MySQL 数据库（本地和 Docker）
- 备份 PostgreSQL 数据库（本地和 Docker）
- 支持多个数据库实例（适用于多个 Docker 项目）
- 备份目录（支持多个）
- 上传到阿里云 OSS / 腾讯云 COS / Backblaze B2

## 使用方法

### 安装依赖

```shell
sudo apt-get install zip -y
```

### 安装 python3

```shell
sudo apt-get install python3 python3-pip -y
pip3 install pyyaml
pip3 install oss2 # 阿里云 oss（可选）
pip3 install cos-python-sdk-v5 # 腾讯云 cos（可选）
pip3 install b2sdk # backblaze b2（可选）
```

### 克隆项目

```sh
git clone https://github.com/forecho/backup-to-cloud-storage.git
```

### 配置

```sh
cd backup-to-cloud-storage && cp config.yaml.example config.yaml
```

编辑 `config.yaml`：

```yaml
backup:
    driver: oss          # oss, cos, 或 b2
    name: myserver       # 备份文件前缀
    src: /var/www/html   # 要备份的目录（空格分隔）
    dir: /tmp/backup     # 临时目录
    password: backup     # zip 密码

# 数据库配置（全部可选，支持多个实例）
databases:
    mysql:
        # 本地 MySQL
        - name: local
          host: localhost
          user: root
          password: root
          databases: db1,db2

        # Docker MySQL（项目 A）
        - name: project_a
          container: project_a_mysql    # Docker 容器名称
          user: root
          password: root
          databases: app_db

    postgres:
        # Docker PostgreSQL（项目 B）
        - name: project_b
          container: project_b_postgres
          user: postgres
          password: secret
          databases: app,analytics

# 云存储配置（选择一个配置）
oss:
    access_key_id: xxx
    access_key_secret: xxx
    endpoint: https://oss-cn-shenzhen.aliyuncs.com
    bucket: backup
```

#### 数据库配置说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 否 | 备份文件名的标识符（例如：`myserver-mysql-project_a-dbname.sql`） |
| `container` | 否 | Docker 容器名称。如果设置，将使用 `docker exec` 进行备份 |
| `host` | 否 | 数据库主机（默认：localhost，使用容器时忽略） |
| `port` | 否 | 数据库端口（仅 PostgreSQL，默认：5432） |
| `user` | 是 | 数据库用户名 |
| `password` | 否 | 数据库密码 |
| `databases` | 是 | 逗号分隔的数据库名称 |

#### 如何获取 Docker 容器名称

```sh
# 列出所有运行中的容器
docker ps

# 输出示例：
# CONTAINER ID   IMAGE          COMMAND                  NAMES
# a1b2c3d4e5f6   mysql:8.0      "docker-entrypoint.s…"   project_a_mysql
# f6e5d4c3b2a1   postgres:15    "docker-entrypoint.s…"   project_b_postgres
```

`NAMES` 列就是您需要的容器名称。如果您使用 docker-compose，容器名称通常是 `{project_directory}_{service_name}_1` 或 `{project_name}-{service_name}-1`。

您也可以在 `docker-compose.yml` 中找到：

```yaml
services:
  db:
    container_name: my_mysql    # <-- 这就是容器名称
    image: mysql:8.0
```

如果未设置 `container_name`，请使用 `docker ps` 检查实际名称。

### 运行

```sh
python3 backup.py
```

## 定时任务（Cron）

```sh
crontab -e
```

添加以下行以在每天凌晨 2:00 运行备份：

```
0 2 * * * /usr/bin/python3 /root/backup-to-cloud-storage/backup.py
```

## 致谢

- [备份 vps 到七牛云存储脚本](https://github.com/ccbikai/backuptoqiniu)
- [阿里云 OSS 官方 SDK](https://github.com/aliyun/aliyun-oss-python-sdk)

