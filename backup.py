# !/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import yaml
import os
import subprocess

def cfg(key, required=True):
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_path, 'config.yaml'), 'r') as f:
        config = yaml.safe_load(f)
    try:
        value = config[key]
    except KeyError:
        if required:
            raise KeyError('Config key "{}" not found!'.format(key))
        return None
    if value is None:
        return None
    return value

def dump_mysql(backup_dir, backup_name, db_config, name_suffix=''):
    """备份 MySQL 数据库（本地或 Docker）"""
    container = db_config.get('container')
    password = db_config.get('password') or ''
    user = db_config['user']
    host = db_config.get('host', 'localhost')
    name = db_config.get('name', name_suffix)
    
    source_type = 'Docker: {}'.format(container) if container else 'Local'
    print('Dumping MySQL ({})...'.format(source_type))
    
    for db in db_config['databases'].split(','):
        db = db.strip()
        filename = '{}-mysql-{}-{}.sql'.format(backup_name, name, db) if name else '{}-mysql-{}.sql'.format(backup_name, db)
        path = '{}/{}'.format(backup_dir, filename)
        with open(path, 'w') as f:
            if container:
                cmd = ['docker', 'exec', container, 'mysqldump', '-u', user, '-p{}'.format(password), db]
            else:
                cmd = ['mysqldump', '-u', user, '-h', host, '-p{}'.format(password), db]
            subprocess.call(cmd, stdout=f)
    print('Dumping MySQL ({}) done!'.format(source_type))

def dump_postgres(backup_dir, backup_name, db_config, name_suffix=''):
    """备份 PostgreSQL 数据库（本地或 Docker）"""
    container = db_config.get('container')
    host = db_config.get('host', 'localhost')
    port = db_config.get('port', '5432')
    user = db_config['user']
    password = db_config.get('password') or ''
    name = db_config.get('name', name_suffix)
    
    source_type = 'Docker: {}'.format(container) if container else 'Local'
    print('Dumping PostgreSQL ({})...'.format(source_type))
    
    env = os.environ.copy()
    if password:
        env['PGPASSWORD'] = password
    
    for db in db_config['databases'].split(','):
        db = db.strip()
        filename = '{}-postgres-{}-{}.sql'.format(backup_name, name, db) if name else '{}-postgres-{}.sql'.format(backup_name, db)
        path = '{}/{}'.format(backup_dir, filename)
        with open(path, 'w') as f:
            if container:
                if password:
                    cmd = ['docker', 'exec', '-e', 'PGPASSWORD={}'.format(password), container, 'pg_dump', '-U', user, db]
                else:
                    cmd = ['docker', 'exec', container, 'pg_dump', '-U', user, db]
                subprocess.call(cmd, stdout=f)
            else:
                cmd = ['pg_dump', '-h', host, '-p', str(port), '-U', user, db]
                subprocess.call(cmd, stdout=f, env=env)
    print('Dumping PostgreSQL ({}) done!'.format(source_type))

def main():
    backup_dir = cfg('backup')['dir']
    backup_name = cfg('backup')['name']
    subprocess.call(['mkdir', '-p', backup_dir])
    
    # MySQL 数据库（支持多个实例）
    databases = cfg('databases', required=False) or {}
    
    mysql_list = databases.get('mysql') or []
    if isinstance(mysql_list, dict):
        mysql_list = [mysql_list]
    for i, db_config in enumerate(mysql_list):
        dump_mysql(backup_dir, backup_name, db_config, name_suffix=str(i) if len(mysql_list) > 1 else '')
    
    # PostgreSQL 数据库（支持多个实例）
    postgres_list = databases.get('postgres') or []
    if isinstance(postgres_list, dict):
        postgres_list = [postgres_list]
    for i, db_config in enumerate(postgres_list):
        dump_postgres(backup_dir, backup_name, db_config, name_suffix=str(i) if len(postgres_list) > 1 else '')

    print('Zipping...')
    backup_name = '{}-backup-{}.zip'.format(cfg('backup')['name'], datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    backup_path = '{}/{}'.format(cfg('backup')['dir'], backup_name)
    backup_src = cfg('backup')['src']
    if backup_src is None:
        backup_src = ''
    os.system('zip -qrP {} {} {} {}'.format(cfg('backup')['password'], backup_path, '{}/*.sql'.format(cfg('backup')['dir']), backup_src))
    print('Zipping done!')

    # upload
    print('Uploading...')
    if cfg('backup')['driver'] == 'oss':
        from oss2 import Auth, Bucket
        auth = Auth(cfg('oss')['access_key_id'], cfg('oss')['access_key_secret'])
        bucket = Bucket(auth, cfg('oss')['endpoint'], cfg('oss')['bucket'])
        bucket.put_object_from_file(backup_name, backup_path)
    elif cfg('backup')['driver'] == 'cos':
        from qcloud_cos import CosConfig
        from qcloud_cos import CosS3Client
        config = CosConfig(Region=cfg('cos')['region'], SecretId=cfg('cos')['secret_id'], SecretKey=cfg('cos')['secret_key'])
        client = CosS3Client(config)
        client.put_object_from_local_file(
            Bucket=cfg('cos')['bucket'],
            LocalFilePath=backup_path,
            Key=backup_name,
        )
    elif cfg('backup')['driver'] == 'b2':
        import b2sdk.v2 as b2
        b2_api = b2.B2Api()
        b2_api.authorize_account('production', cfg('b2')['application_key_id'], cfg('b2')['application_key'])
        bucket = b2_api.get_bucket_by_name(cfg('b2')['bucket'])
        bucket.upload_local_file(
            local_file=backup_path,
            file_name=backup_name,
        )

    print('Cleaning...')
    subprocess.call(['rm', '-rf', cfg('backup')['dir']])

if __name__ == '__main__':
    main()
