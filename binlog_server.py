#!/usr/bin/python
# -*- coding: utf8 -*-
"""
Usage:
        binlog_server.py --user=<username> --password=<password> --host=<remote_host> --port=<remote_port> --backup-dir=<backup_dir> --log=<log> [--last-file=<last-file>] [--stop-never-slave-server-id]
        binlog_server.py make-config --info-file=<server.csv> [--delimiter=<','>] [--quotechar=<'"'>] --config-file=<binlog_server.cnf> [--start-from=<mysql-bin.000001>]
        binlog_server.py -h | --help
        binlog_server.py --version
        binlog_server.py --config=<config_file> --dbname=<database_name> [--last-file=<last-file>]

Options:
        -h --help                               Show help information.
        --version                               Show version.
        --user=<username>                       The user name used to connect to the remote server.
        --password=<password>                   The password used to connect to the remote server.
        --host=<remote_host>                    The remote host IP address.
        --port=<remote_port>                    The remote MySQL server port.
        --backup-dir=<backup_dir>               The dest to store binlog.
        --log=<log>                             The log.
        --last-file=<last-file>                 Specify the starting binlog.
        --config=<config_file>                  Config file.
        --dbname=<database_name>                Section name in config file.
        --stop-never-slave-server-id            The slave server_id used for binlog server.
        --info-file=<./server.csv>              The file contained the MySQL info which mysqlbinlog needed [default ./server.csv].
        --delimiter=<','>                       The info file's delimiter [default ','].
        --quotechar=<'"'>                       The info file's quotechar [default '"'].
        --config-file=<./binlog_server.cnf>     The configuration file to be generated [default ./binlog_server.cnf].
        --start-from                            The --last-file in Bootstrap scripts.[default mysql-bin.000001]
"""

import subprocess
import logging
import time
import ConfigParser
import os
import csv

from docopt import docopt


#['ceshi','192.168.3.100', '3307', 'binlog_backup', '123', '', '', '']
#['ceshi','192.168.3.100', '3307', 'binlog_backup', '123', '/bak/', 'aa.log', '']
def genConfig(config_file,info_file,delimiter=',',quotechar='"'):
    cf=ConfigParser.ConfigParser()
    cf.read(config_file)
    section_list = []
    with open(info_file,'rb') as csvfile:
        info = csv.reader(csvfile,delimiter=delimiter,quotechar=quotechar)
        for row in info:
            if not row[0]:
                section_name = row[1].replace('.','',4)
            else:
                section_name = row[0]
            db_host, db_port, db_user, db_passwd, server_id = row[1],row[2],row[3],row[4],row[7]
            
            if not db_host or not db_port or not db_user or not db_passwd:
                print('csv文件有错误')

            if row[5][-1] != '/':
                backup_dir = row[5] + '/' + row[1] + '/'
            else:
                backup_dir = row[5] + row[1] + '/'
            
            if not row[6]:
                print(row[1] + ' 默认日志为 ' + row[1] + '.log')
                log = backup_dir + row[1] + '.log'
            else:
                log = backup_dir + row[6]
            cf.add_section(section_name)
            cf.set(section_name, 'db_host', db_host)
            cf.set(section_name, 'db_port', db_port)
            cf.set(section_name, 'db_user', db_user)
            cf.set(section_name, 'db_passwd', db_passwd)
            cf.set(section_name, 'backup_dir', backup_dir)
            cf.set(section_name, 'log', log)
            cf.set(section_name, 'server_id', server_id)
            section_list.append([section_name,db_host,backup_dir])
    with open(config_file,'w') as f:
        cf.write(f)
    return section_list

def genStartupComm(section_list,config_file,start_from='mysql-bin.000001'):
    with open(os.getcwd()+'/bootstrap_'+os.path.basename(config_file).split('.')[0]+'.sh','w') as file:
        for line in section_list:
            file.write('nohup python /scripts/binlog_server.py --config='+ os.path.realpath(config_file) + ' --dbname='+ line[0] + ' --last-file=' + start_from + ' &' + '\n')
    with open(os.getcwd()+'/crontab_'+os.path.basename(config_file).split('.')[0]+'.sh','w') as file:
        for line in section_list:
            file.write('*/5 * * * * sh  /scripts/mon_binlog_server.sh ' + line[0] + ' ' + line[1] + ' >> /scripts/mon_' + line[0] + '_binserver.log 2>&1' + '\n')

def mkdir(backup_dir):
    if backup_dir[-1]!= '/':
        print('backup_dir must end with /')
        os.exit()
    if not os.path.isdir(backup_dir):
        os.makedirs(backup_dir)

def dumpBinlog(user,password,host,port,backup_dir,log,last_file='',server_id=''):
        LOCAL_BACKUP_DIR=backup_dir

        #BACKUP_LOG='/data4/binlog_backup/120.27.136.247/BB.log'
        BACKUP_LOG=log[log.rfind('/')+1:]
        while True:
            if not last_file:
                    #cmd="ls -A {LOCAL_BACKUP_DIR} | grep -v {BACKUP_LOG} | grep -v nohup.out |wc -l".format(LOCAL_BACKUP_DIR=LOCAL_BACKUP_DIR,BACKUP_LOG=BACKUP_LOG)
                    cmd="ls -A {LOCAL_BACKUP_DIR} | grep -E mysql-bin\.[0-9]*$ | wc -l".format(LOCAL_BACKUP_DIR=LOCAL_BACKUP_DIR)
                    print(cmd)
                    child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    child.wait()
                    wc_l=int(child.communicate()[0].strip())
                    print(wc_l)
                    if wc_l != 0:
                            #cmd="ls -l %s | grep -v %s | grep -v nohup.out |tail -n 1 |awk '{print $9}'" % (LOCAL_BACKUP_DIR,BACKUP_LOG)
                            cmd="ls -l %s | grep -E mysql-bin\.[0-9]*$ |tail -n 1 |awk '{print $9}'" % (LOCAL_BACKUP_DIR)
                            print(cmd)
                            child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            child.wait()
                            LAST_FILE=child.communicate()[0].strip()
                            print(LAST_FILE)
            else:
                    LAST_FILE=last_file
                    print(LAST_FILE)
            logging.info('Last File is %s' % (LAST_FILE))

            if not server_id:
                mysqlbinlog='/usr/local/mysql/bin/mysqlbinlog --raw --read-from-remote-server --stop-never --host={REMOTE_HOST} --port={REMOTE_PORT} --user={REMOTE_USER} --password={REMOTE_PASS} --result-file={RESULT_FILE} {LAST_FILE}'.format(REMOTE_HOST=host,REMOTE_PORT=port,REMOTE_USER=user,REMOTE_PASS=password,RESULT_FILE=LOCAL_BACKUP_DIR,LAST_FILE=LAST_FILE)
                print(mysqlbinlog)
            elif server_id:
                mysqlbinlog='/usr/local/mysql/bin/mysqlbinlog --raw --read-from-remote-server --stop-never --host={REMOTE_HOST} --port={REMOTE_PORT} --user={REMOTE_USER} --password={REMOTE_PASS} --stop-never-slave-server-id={SERVER_ID} --result-file={RESULT_FILE} {LAST_FILE}'.format(REMOTE_HOST=host,REMOTE_PORT=port,REMOTE_USER=user,REMOTE_PASS=password,SERVER_ID=server_id,RESULT_FILE=LOCAL_BACKUP_DIR,LAST_FILE=LAST_FILE)
                print(mysqlbinlog)

            #subprocess.call(mysqlbinlog,shell=True)
            child = subprocess.Popen(mysqlbinlog, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while child.poll() == None:
                stdout_line = child.stdout.readline().strip()
                if stdout_line:
                    logging.info(stdout_line)
            logging.info(child.stdout.read().strip())
            logging.info('Binlog server stop!!!,reconnect after 10 seconds')
            last_file=None
            time.sleep(10)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Binlog server 0.3.0')
    print(arguments)

    if arguments['make-config']:
        if not arguments['--delimiter']:
            delimiter = ','
        else:
            delimiter = arguments['--delimiter']
        if not arguments['--quotechar']:
            quotechar = '"'
        else:
            quotechar = arguments['--quotechar']

        section_list = genConfig(arguments['--config-file'],arguments['--info-file'],delimiter,quotechar)
        if not arguments['--start_from']:
            genStartupComm(section_list,arguments['--config-file'])
        else:
            genStartupComm(section_list,arguments['--config-file'],arguments['--start_from'])
    else:
        if arguments['--config']:
            cf=ConfigParser.ConfigParser()
            cf.read(arguments['--config'])
            section_name = arguments['--dbname']
            db_host = cf.get(section_name, "db_host")
            db_port = cf.get(section_name, "db_port")
            db_user = cf.get(section_name, "db_user")
            db_passwd = cf.get(section_name, "db_passwd")
            backup_dir = cf.get(section_name, "backup_dir")
            server_id = cf.get(section_name, "server_id")
            log = cf.get(section_name, "log")

            mkdir(backup_dir)
            logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=log,
                        filemode='a')
            lock_file=db_host+"_binlog_server.lock"
        else:
            mkdir(arguments['--backup-dir'])
            logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=arguments['--log'],
                        filemode='a')
            lock_file=arguments['--host']+"_binlog_server.lock"


        child=subprocess.Popen('ls /tmp|grep %s' % (lock_file),shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        child.wait()
        lock=child.communicate()[0].strip()
        print(lock)
        if not lock:
            subprocess.call('touch /tmp/%s' % (lock_file),shell=True)
            logging.info('Get lock,Binlog server start!!!')
            if not arguments['--config']:
               dumpBinlog(arguments['--user'],arguments['--password'],arguments['--host'],arguments['--port'],arguments['--backup-dir'],arguments['--log'],arguments['--last-file'],arguments['--stop-never-slave-server-id'])
            else:
               dumpBinlog(db_user,db_passwd,db_host,db_port,backup_dir,log,arguments['--last-file'],server_id)
        else:
            logging.info('Binlog server already running!!!')
            print('Binlog server already running!!!,please check or reomove the lock file')
