# backupToOSS

备份到阿里云的 OSS

## 如何使用

1. 下载代码
2. 修改 `backup.sh` 文件配置
3. 给 `./backup.sh` 添加执行权限, `chmod +x backup.sh`

## 添加定时任务

```
$ crontab -e
```

进入 cron 编辑，按 `i` 进入编辑模式，在最后输入以下内容（以下示例为每天凌晨02:00执行备份，请确认脚本路径）

```
0 2 * * * /root/backup/backup.sh
```

## 感谢

感谢[备份vps到七牛云存储脚本](https://github.com/ccbikai/backuptoqiniu)的代码。