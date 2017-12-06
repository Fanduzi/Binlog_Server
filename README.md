# Binlog_Server

## 同步binlog方法
两种方式

1.通过配置文件
```
python /scripts/binlog_server.py --config=/tmp/binlog_server.cnf --dbname=GN_PT_SLAVE1
```
2.命令行指定
注意backup-dir一定要以'/'结尾
```
python binlog_server.py --user=binlog_backup --password=xxxx --host=xxxx --port=3306 --backup-dir=/data4/binlog_backup/ --log=/data4/binlog_backup/BB.log
```
在脚本中 创建了/tmp/IP__binlog_server.lock 文件,为了防止重复运行. 
如果有需要停止,需要手动kill binlog_server.py 和 mysqlbinlog, 并且删除/tmp/IP__binlog_server.lock 文件,不然下次起不来

## 生成配置文件和启动脚本方法

```
python /scripts/binlog_server.py make-config --info-file=info.csv --config-file=binlog_server.cnf
```
info-file内容:
```
#section_name, db_host, db_port, db_user, db_passwd, backup_dir, log, server_id
'ceshi','192.168.3.100', '3307', 'binlog_backup', '123', '', '', ''
```

### 配置文件
```
[root@localhost 120.27.143.36]# less /scripts/binlog_server.cnf 
[GN_PT_SLAVE1]
db_host=120.27.136.888
db_port=3306
db_user=binlog_backup
db_passwd=xxxx
backup_dir=/data1/backup/db_backup/120.27.136.888/ --注意一定要以/结尾
log=/data1/backup/db_backup/120.27.136.888/BB.log

[GN_LOG_MASTER2]
db_host=120.27.143.999
db_port=3306
db_user=binlog_backup
db_passwd=xxxx
backup_dir=/data2/backup/db_backup/120.27.143.999/ --注意一定要以/结尾
log=/data2/backup/db_backup/120.27.143.999/BB.log
```

