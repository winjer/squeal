#
# Regular cron jobs for the squeal package
#
0 4	* * *	root	[ -x /usr/bin/squeal_maintenance ] && /usr/bin/squeal_maintenance
