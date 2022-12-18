# !/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import yaml
import os
import subprocess

def cfg(key):
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_path, 'config.yaml'), 'r') as f:
        config = yaml.safe_load(f)
    try:
        value = config[key]
    except KeyError:
        raise KeyError('Config key "{}" not found!'.format(key))
    if value is None:
        return ''
    return value

def main():
    # dump mysql
    print('Dumping mysql...')
    password = cfg('mysql')['password']
    if password is None:
        password = ''
    subprocess.call(['mkdir', '-p', cfg('backup')['dir']])
    for db in cfg('mysql')['databases'].split(','):
        path = '{}/{}-{}.sql'.format(cfg('backup')['dir'], cfg('backup')['name'], db)
        with open(path, 'w') as f:
            subprocess.call(['mysqldump', '-u', cfg('mysql')['user'], '-h', cfg('mysql')['host'], '-p{}'.format(password), db], stdout=f)
    print('Dumping mysql done!')

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
    # subprocess.call(['rm', '-rf', cfg('backup')['dir']])

if __name__ == '__main__':
    main()
