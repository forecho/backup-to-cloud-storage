# backup to Cloud Storage

[![Build Status](https://travis-ci.org/forecho/backup-to-cloud-storage.svg?branch=master)](https://travis-ci.org/forecho/backup-to-cloud-storage)

Backup your database and files to Cloud Storage.

## What can it do?

- Backup MySQL database
- Backup directory (multiple)

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
cd backup-to-cloud-storage && cp config.example.yml config.yml
```


### Run

```sh
python3 backup.py
```

## Cron

```sh
$ crontab -e
```

add this line

```
0 2 * * * /usr/bin/python3 /root/backup-to-cloud-storage/backup.py
```

## Thanks

- [备份 vps 到七牛云存储脚本](https://github.com/ccbikai/backuptoqiniu)
- [阿里云 OSS 官方 SDK](https://github.com/aliyun/aliyun-oss-python-sdk)
