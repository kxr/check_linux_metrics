# check_linux_metrics.py
A monitoring plugin for icinga/nagios/nsca, that reports basic system metrics of a linux host: cpu, load, threads, openfiles, procs, diskio, disku, memory, swap, network

## Key features

 - **Minimal dependency:** Only needs basic python libraries which are installed by default on linux, all the metrics are calculated from the /proc filesystem

 - **Minimal privilege:**  Can be run by any non-priviliged user. Does not require root

 - **No Sampling:** Important metrics like CPU, DiskIO, NetworkIO and new process forks are calculated based on the cumulative values provided by the kernel. These cumulative values are provided by the kernel since uptime, when any of these checks are called the first time, the values are copied in the interim directory. Next time whenever the plugin is called, the diffrential/interim values are reported. This ensures that there is no peak/spike missed in between the plugin calls.

## TODO
 - Improve and stanadardize argument handling
 - Print usage instructions if wrong/bad arguments are passed
 - Add more sanity checks for arguments
 - Add more warning and critical thresholds
 - Move the output printing part from each function to a single function
 - Enable/disable perfdata
 - Add a file age plugin?
 - Add a Process wise memory and cpu usage reporting function?
 - Add functionality of directly sending email (making this script usefull as a standalone monitoring)
 - Add graphite output support?
 
## Program Structure

  The Main function checks and validate arguments and call the respective independent functions check_cpu etc.

## Usage Examples
 - CPU
`<script> cpu [warn%] [critical%]`

        [user@localhost ~]$ ./check_linux_metrics.py cpu
        This was the first run, run again to get values

        [user@localhost ~]$ ./check_linux_metrics.py cpu
        CPU Usage: 7.57% [t:60.04] | cpu=7.57% user=1.00% system=0.54% iowait=5.97% nice=0.04% irq=0.00% softirq=0.01% steal=0.00%

        [user@localhost ~]$ ./check_linux_metrics.py cpu 80 99
        CPU Usage: 9.17% [t:60.13] (OK) | cpu=9.17%;80;99 user=1.01%;80;99 system=0.55%;80;99 iowait=7.54%;80;99 nice=0.05%;80;99 irq=0.00%;80;99 softirq=0.02%;80;99 steal=0.00%;80;99

 - Load
     `<script> load [warn(load1,load5,load15)] [critical(load1,load5,load15)]`
        [user@localhost ~]$ ./check_linux_metrics.py load
        Load1: 0.34 Load5: 0.36 Load15: 0.36 | load1=0.34 load5=0.36 load15=0.36

        [user@localhost ~]$ ./check_linux_metrics.py load 7,6,5 20,15,10
        Load1: 0.34 Load5: 0.36 Load15: 0.36 (OK) (OK) (OK) | load1=0.34;7;20 load5=0.36;6;15 load15=0.36;5;10

        [user@localhost ~]$ ./check_linux_metrics.py load 7 20
        Load1: 0.34 Load5: 0.36 Load15: 0.36 (OK) | load1=0.34;7;20 load5=0.36 load15=0.36

        [user@localhost ~]$ ./check_linux_metrics.py load ,6, ,15,
        Load1: 0.34 Load5: 0.36 Load15: 0.36 (OK) | load1=0.34;; load5=0.36;6;15 load15=0.36;;

        [user@localhost ~]$ ./check_linux_metrics.py load ,,5 ,,10
        Load1: 0.34 Load5: 0.36 Load15: 0.36 (OK) | load1=0.34;; load5=0.36;; load15=0.36;5;10

 - Threads
     `<script> threads [warn#] [critical#]`
        [user@localhost ~]$ ./check_linux_metrics.py threads
        Threads: 1/207  | running=1.00 total=207.00

        [user@localhost ~]$ ./check_linux_metrics.py threads 10 50
        Threads: 1/207  (OK) | running=1.00;10;50 total=207.00

 - Open Files
     `<script> files [warn#] [critical#]`
        [user@localhost ~]$ ./check_linux_metrics.py files
        Open Files: 1344 (free: 0) | open=1344.00 free=0.00

        [user@localhost ~]$ ./check_linux_metrics.py files 5000 50000
        Open Files: 1344 (free: 0) (OK) | open=1344.00;5000;50000;0;1202794 free=0.00

 - Processes
     `<script> procs [warn#(total,running,waiting)] [critical#(total,running,waiting)]`
        [user@localhost ~]$ ./check_linux_metrics.py procs
        This was the first run, run again to get values

        [user@localhost ~]$ ./check_linux_metrics.py procs
        Total:149 Running:1 Sleeping:148 Waiting:0 Zombie:0 Others:0 New_Forks:4.55/s | total=149.00 forks=4.55 sleeping=148.00 running=1.00 waiting=0.00 zombie=0.00 others=0.00

        [user@localhost ~]$ ./check_linux_metrics.py procs 500,16,8 1500,32,16
        Total:149 Running:1 Sleeping:148 Waiting:0 Zombie:0 Others:0 New_Forks:4.78/s (OK) (OK) (OK) | total=149.00;500;1500 forks=4.78 sleeping=148.00 running=1.00;16;32 waiting=0.00;8;16 zombie=0.00 others=0.00

        [user@localhost ~]$ ./check_linux_metrics.py procs 500 1500
        Total:149 Running:1 Sleeping:148 Waiting:0 Zombie:0 Others:0 New_Forks:4.40/s (OK) | total=149.00;500;1500 forks=4.40 sleeping=148.00 running=1.00 waiting=0.00 zombie=0.00 others=0.00

        [user@localhost ~]$ ./check_linux_metrics.py procs ,,8 ,,16
        Total:149 Running:1 Sleeping:147 Waiting:1 Zombie:0 Others:0 New_Forks:4.73/s (OK) | total=149.00;; forks=4.73 sleeping=147.00 running=1.00;; waiting=1.00;8;16 zombie=0.00 others=0.00

        [user@localhost ~]$ ./check_linux_metrics.py procs ,16, ,32,
        Total:149 Running:1 Sleeping:148 Waiting:0 Zombie:0 Others:0 New_Forks:4.52/s (OK) | total=149.00;; forks=4.52 sleeping=148.00 running=1.00;16;32 waiting=0.00;; zombie=0.00 others=0.00

 - Disk IO
     `<script> diskio block_device [warn(read,write)] [critical(read,write)]`
     note: unit is sectors/sec
        [user@localhost ~]$ ./check_linux_metrics.py diskio /dev/cciss/c0d0
        This was the first run, run again to get values: diskio(cciss/c0d0)

        [user@localhost ~]$ ./check_linux_metrics.py diskio /dev/cciss/c0d0
        /dev/cciss/c0d0(cciss/c0d0) Read: 0.00 sec/s (0.00 t/s) Write: 785.82 sec/s (63.47 t/s) [t:60.04] | read_operations=0.00 read_sectors=0.00 read_time=0.00 write_operations=63.47 write_sectors=785.82 write_time=18868.11

        [user@localhost ~]$ ./check_linux_metrics.py diskio /dev/cciss/c0d0 50,100 200,250
        /dev/cciss/c0d0(cciss/c0d0) Read: 0.00 sec/s (0.00 t/s) Write: 765.68 sec/s (55.47 t/s) [t:60.05] (Critical) | read_operations=0.00 read_sectors=0.00;50;200 read_time=0.00 write_operations=55.47 write_sectors=765.68;100;250 write_time=15716.77

        [user@localhost ~]$ ./check_linux_metrics.py diskio /dev/mapper/VolGroup-lv_root
        This was the first run, run again to get values: diskio(dm-0)

        [user@localhost ~]$ ./check_linux_metrics.py diskio /dev/mapper/VolGroup-lv_root
        /dev/mapper/VolGroup-lv_root(dm-0) Read: 0.00 sec/s (0.00 t/s) Write: 1016.04 sec/s (127.01 t/s) [t:60.04] | read_operations=0.00 read_sectors=0.00 read_time=0.00 write_operations=127.01 write_sectors=1016.04 write_time=31707.88

        [user@localhost ~]$ ./check_linux_metrics.py diskio /dev/VolGroup/lv_root
        /dev/VolGroup/lv_root(dm-0) Read: 0.00 sec/s (0.00 t/s) Write: 1074.80 sec/s (134.35 t/s) [t:60.04] | read_operations=0.00 read_sectors=0.00 read_time=0.00 write_operations=134.35 write_sectors=1074.80 write_time=34072.15

 - Disk Usage
     `<script> disku [warn%] [critical%]`
        [user@localhost ~]$ ./check_linux_metrics.py disku /
        / Used: 76.45 GB / 196.74 GB (38.86%) | used=38.86%

        [user@localhost ~]$ ./check_linux_metrics.py disku / 75 90
        / Used: 76.45 GB / 196.74 GB (38.86%) (OK) | used=38.86%;75;90

        [user@localhost ~]$ ./check_linux_metrics.py disku /boot 75 90
        /boot Used: 0.10 GB / 0.47 GB (21.32%) (OK) | used=21.32%;75;90

        [user@localhost ~]$ ./check_linux_metrics.py disku /var 75 90
        Plugin Error: Mount point not valid: (/var)

- Memory
     `<script> memory [warn%] [critical%]`
     note: used memory is calculated as: total - free - cached
        [user@localhost ~]$ ./check_linux_metrics.py memory
        Memory Used: 786.41MB / 11845.97MB (6.64%) | used=786.41;;;0;11845 cached=10911.13 active=7144.62

        [user@localhost ~]$ ./check_linux_metrics.py memory 75 90
        Memory Used: 786.90MB / 11845.97MB (6.64%) (OK) | used=786.90;8884;10661;0;11845 cached=10911.13 active=7144.82

- Swap
     `<script> cpu [warn%] [critical%]`
     note: used cached is calculated as: total - free - cached
        [user@localhost ~]$ ./check_linux_metrics.py swap
        Swap Used: 0.11MB / 5992.00MB (0.00%) | used=0.11;;;0;5991 cached=0.18

        [user@localhost ~]$ ./check_linux_metrics.py swap 75 90
        Swap Used: 0.11MB / 5992.00MB (0.00%) (OK) | used=0.11;4493;5392;0;5991 cached=0.18

- Network
     `<script> network device [warn(rx,tx)] [critical(rx,tx)]`
     note: unit is MB/s
        [user@localhost ~]$ ./check_linux_metrics.py network eth0
        This was the first run, run again to get values: net:eth0

        [user@localhost ~]$ ./check_linux_metrics.py network eth0
        eth0 Rx: 0.01 MB/s (16.74 p/s) Tx: 0.00 MB/s (11.16 p/s) [t:60.04] | RX_MBps=0.01 RX_PKps=16.74 TX_MBps=0.00 TX_PKps=11.16 PK_ERRORS=0.00

        [user@localhost ~]$ ./check_linux_metrics.py network eth0 30,50 60,80
        eth0 Rx: 0.01 MB/s (17.80 p/s) Tx: 0.00 MB/s (11.62 p/s) [t:60.05] (OK) | RX_MBps=0.01;30;60 RX_PKps=17.80 TX_MBps=0.00;50;80 TX_PKps=11.62 PK_ERRORS=0.00
