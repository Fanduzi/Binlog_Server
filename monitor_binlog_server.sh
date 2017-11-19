#!/bin/bash
num_py=`ps -ef | grep binlog_server.py | grep -v grep | grep $1 | wc -l`
num_mysqlbinlog=`ps -ef | grep mysqlbinlog | grep -v grep | grep $2 | wc -l`
TO_MAIL=fanboshi@longtugame.com
if [ $num_py -eq 0 ] && [ $num_mysqlbinlog -eq 0 ];then
        #发邮件,$1 binlog server宕了
        #重启 nohup python /scripts/binlog_server.py --config=/tmp/binlog_server.cnf --dbname=$1 &
        echo "新备份机 $1 binlog server宕了" |/usr/bin/mutt -s "Binlog server监控告警" $TO_MAIL
elif [ $num_py -eq 0 ] && [ $num_mysqlbinlog -eq 1 ];then
        #发邮件,$1 python脚本挂了,但是mysqlbinlog还在跑
        echo "新备份机 $1 python脚本挂了,但是mysqlbinlog还在跑" |/usr/bin/mutt -s "Binlog server监控告警" $TO_MAIL
elif [ $num_py -eq 1 ] && [ $num_mysqlbinlog -eq 0 ];then
        #发邮件,$1 python脚本还在跑,但是mysqlbinlog挂了
        echo "新备份机 $1 python脚本还在跑,但是mysqlbinlog挂了" |/usr/bin/mutt -s "Binlog server监控告警" $TO_MAIL
fi
