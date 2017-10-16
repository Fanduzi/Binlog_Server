#!/bin/bash
num_py=`ps -ef | grep binlog_server.py | grep -v grep | grep GN_PT_SLAVE1 | wc -l`
num_mysqlbinlog=`ps -ef | grep mysqlbinlog | grep -v grep | grep 120.27.136.247 | wc -l`
TO_MAIL=fanboshi@longtugame.com
if [ $num_py -eq 0 ] && [ $num_mysqlbinlog -eq 0 ];then
        #发邮件,GN_PT_SLAVE1 binlog server宕了
        #重启 nohup python /scripts/binlog_server.py --config=/tmp/binlog_server.cnf --dbname=GN_PT_SLAVE1 &
        echo "GN_PT_SLAVE1 binlog server宕了" |/usr/bin/mutt -s "Binlog server监控告警" $TO_MAIL
elif [ $num_py -eq 0 ] && [ $num_mysqlbinlog -eq 1 ];then
        #发邮件,GN_PT_SLAVE1 python脚本挂了,但是mysqlbinlog还在跑
        echo "GN_PT_SLAVE1 python脚本挂了,但是mysqlbinlog还在跑" |/usr/bin/mutt -s "Binlog server监控告警" $TO_MAIL
fi
