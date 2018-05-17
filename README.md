[![Author](https://img.shields.io/badge/author-Fan()-blue.svg?style=flat)](http://fuxkdb.com/)

# Binlog_Server
首先
`pip install docopt==0.6.2 pymysql filelock`

然后你应该使用 -h 查看帮助信息

## 同步binlog方法
两种方式

- 1.通过配置文件启动
```
nohup python /scripts/binlog_server.py --config=/tmp/binlog_server.cnf --dbname=GN_PT_SLAVE1 --last-file=mysql-bin.00001 &
```
- 2.命令行指定

注意backup-dir一定要以'/'结尾
```
nohup python binlog_server.py --user=binlog_backup --password=xxxx --host=xxxx --port=3306 --backup-dir=/data4/binlog_backup/ --log=/data4/binlog_backup/BB.log --last-file=mysql-bin.00001 &
```
使用--last-file手动指定binlog server起始文件. 如果没指定则默认会去找backup-dir下最后一个作为起点

在脚本中 为了防止重复运行,启动binlog server时会创建了/tmp/IP__binlog_server.lock 文件.

如果有需要停止,需要手动kill binlog_server.py 和 mysqlbinlog, 并且删除/tmp/IP__binlog_server.lock 文件,不然下次起不来

## 生成配置文件和启动脚本方法

当你需要部署几十上百个binlog server时,就需要用到make-config命令了.
首先创建一个包含服务器信息的csv文件
```
[root@cn_mu_binlog_backup scripts]# less android.csv 
"40001","10.241.3.xxx","3306","loguser","youpassword","/data/app1_binlog_backup/android/40001/","40001.log","40001"
"40002","10.241.3.xxx","3306","loguser","youpassword","/data/app1_binlog_backup/android/40002/","40002.log","40002"
"40003","10.241.3.xxx","3306","loguser","youpassword","/data/app1_binlog_backup/android/40003/","40003.log","40003"
"40004","10.241.3.xxx","3306","loguser","youpassword","/data/app1_binlog_backup/android/40004/","40004.log","40004"
```
第一列对应配置文件中的section,如果为空("")则为ip地址

2,3,4,5无需解释

第六列为binlog存储路径,如果目录不存在则会自动创建, 注意要以'/'结尾(虽然我好像在脚本中加了判断)

第七列为日志名称,默认存储在备份目录下

第八列为 mysqlbinlog的 --stop-never-slave-server-id 参数值, 可以为空(""),为空则不指定该参数

然后使用如下命令生成配置文件
```
python /scripts/binlog_server.py make-config --info-file=app1.csv --config-file=app1.cnf
```
如果 app1.cnf 已经存在,则需要你手动清空他或删除,我没有在代码里做处理

命令执行成功后会在当前目录生成下列文件
```
# ls | grep android
android.cnf
bootstrap_android.sh
crontab_android.sh
```

内容如下(目前用的nohup &, 其实用supervisor更好一些)
```
[root@cn_mu_binlog_backup scripts]# head -10 android.cnf 
[40001]
db_host = 10.241.0.999
db_port = 3306
db_user = loguser
db_passwd = xxx
backup_dir = /data/app1_binlog_backup/android/40001/10.241.0.999/
log = /data/app1_binlog_backup/android/40001/10.241.0.999/40001.log
server_id = 40001

[40002]
[root@cn_mu_binlog_backup scripts]# head -10 bootstrap_android.sh    --如果没指定--start-from,则默认--last-file=mysql-bin.000001
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40001 --last-file=mysql-bin.000001 &
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40002 --last-file=mysql-bin.000001 &
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40003 --last-file=mysql-bin.000001 &
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40004 --last-file=mysql-bin.000001 &
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40005 --last-file=mysql-bin.000001 &
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40006 --last-file=mysql-bin.000001 &
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40007 --last-file=mysql-bin.000001 &
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40008 --last-file=mysql-bin.000001 &
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40009 --last-file=mysql-bin.000001 &
nohup python /scripts/binlog_server.py --config=/scripts/android.cnf --dbname=40010 --last-file=mysql-bin.000001 &
[root@cn_mu_binlog_backup scripts]# head -10 crontab_android.sh
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40001 10.241.0.xxx >> /scripts/mon_40001_binserver.log 2>&1
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40002 10.241.0.xxx >> /scripts/mon_40002_binserver.log 2>&1
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40003 10.241.0.xxx >> /scripts/mon_40003_binserver.log 2>&1
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40004 10.241.0.xxx >> /scripts/mon_40004_binserver.log 2>&1
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40005 10.241.0.xxx >> /scripts/mon_40005_binserver.log 2>&1
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40006 10.241.0.xxx >> /scripts/mon_40006_binserver.log 2>&1
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40007 10.241.0.xxx >> /scripts/mon_40007_binserver.log 2>&1
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40008 10.241.0.xxx >> /scripts/mon_40008_binserver.log 2>&1
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40009 10.241.0.xxx >> /scripts/mon_40009_binserver.log 2>&1
*/5 * * * * sh  /scripts/mon_binlog_server.sh 40010 10.241.0.xxx >> /scripts/mon_40010_binserver.log 2>&1
```

接下来你就可以使用

sh bootstrap_android.sh 来启动binlog server

crontab_android.sh 中为可以添加到crontab的定时监控任务可以监控各个binlog server运行状态 (里面会用到mutt,自己装)

### 配置文件示例
```
[root@localhost 120.27.143.36]# less /scripts/binlog_server.cnf 
[GN_PT_SLAVE1]
db_host=120.27.136.888
db_port=3306
db_user=binlog_backup
db_passwd=xxxx
backup_dir=/data1/backup/db_backup/120.27.136.888/ --注意一定要以/结尾
log=/data1/backup/db_backup/120.27.136.888/BB.log
server_id=

[GN_LOG_MASTER2]
db_host=120.27.143.999
db_port=3306
db_user=binlog_backup
db_passwd=xxxx
backup_dir=/data2/backup/db_backup/120.27.143.999/ --注意一定要以/结尾
log=/data2/backup/db_backup/120.27.143.999/BB.log
server_id=191037
```

