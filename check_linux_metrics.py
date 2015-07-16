#!/usr/bin/env python

# File: check_linux_metrics.py
# URL: https://github.com/kxr/check_linux_metrics
# Author: Khizer Naeem 
# Email: khizernaeem@gmail.com
# Release 0.1: 20/05/2015
# Release 0.2: 02/06/2015
# Release 0.3: 16/07/2015
# 
#
#  Copyright (c) 2015 Khizer Naeem (http://kxr.me)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import time
import os
import shutil

INTERIM_DIR = '/var/tmp/linux_metrics'
if not os.path.exists(INTERIM_DIR):
	os.makedirs( INTERIM_DIR )


def check_cpu( warn=None, crit=None ):
	status_code = 3
	status_outp =''
	perfdata = ''

	#Verify if the interim file exists, if not create it now
	interim_file = INTERIM_DIR + '/' + 'proc_stat'
	if not os.path.isfile( interim_file ):
		shutil.copyfile( '/proc/stat', interim_file )
		print ( 'This was the first run, run again to get values' )
		exit( 0 )

	# Get mtime of the interim file and calculate the sample period
	sample_period = float( time.time() - os.path.getmtime( interim_file ) )

	# Get the deltas proc stats: interimfile - procfile(now)	
	#with open( interim_file ) as f1:
	f1 = open( interim_file, 'r' )
	try:
		line1 = f1.readline()
	finally:
		f1.close()
	#with open( '/proc/stat' ) as f2:
	f2 = open( '/proc/stat', 'r' )
	try:
		line2 = f2.readline()
	finally:
		f2.close()
	deltas = [int(b) - int(a) for a, b in zip(line1.split()[1:], line2.split()[1:])]
	total = sum( deltas )
	percents = [100 - (100 * (float(total - x) / total)) for x in deltas]

	if len ( percents ) >= 7:
		cpu_pcts = {
		'user': percents[0],
		'nice': percents[1],
		'system': percents[2],
		'idle': percents[3],
		'iowait': percents[4],
		'irq': percents[5],
		'softirq': percents[6]
		}
	# older kernel don't provide steal
	if len ( percents ) >= 8:
		cpu_pcts['steal'] = percents[7]
	else:
		cpu_pcts['steal'] = 0
	cpu_pcts['cpu'] = 100 - cpu_pcts['idle']
	
	#status_outp = 'CPU Usage: ' + format( cpu_pcts['cpu'], '.2f' ) + '%' + ' [t:' + format( sample_period, '.2f' ) + ']'
	status_outp = 'CPU Usage: ' + str( '%.2f' % cpu_pcts['cpu'] ) + '%' + ' [t:' + str( '%.2f' % sample_period ) + ']'

	if warn is not None and crit is not None:
		if float( cpu_pcts['cpu'] ) >= float( crit ):
			status_code = 2
			status_outp += ' (Critical)'
		elif float( cpu_pcts['cpu'] ) >= float( warn ):
			status_code = 1
			status_outp += ' (Warning)'
		else:
			status_code = 0
			status_outp += ' (OK)'
	else:
		status_code = 0

	for x in [ 'cpu', 'user', 'system', 'iowait', 'nice', 'irq', 'softirq', 'steal'  ]:
		#perfdata += x + '=' + format( cpu_pcts[x], '.2f' ) + '%' 
		perfdata += x + '=' + str( '%.2f' % cpu_pcts[x] ) + '%' 
		if warn is not None and crit is not None:
			perfdata += ';' + str(warn) + ';' + str(crit)
		perfdata += ' '
	#remove last space
	perfdata = perfdata[:-1]

	#update the interim file
	shutil.copyfile( '/proc/stat', interim_file )

	print status_outp + ' | ' + perfdata
	exit ( status_code )

def check_load( warn=None, crit=None ):
	status_code = 3
	status_outp =''
	perfdata = ''

	#with open('/proc/loadavg') as f:
	f = open('/proc/loadavg', 'r')
	try:
		line = f.readline()
	finally:
		f.close()
	load_avgs = [float(x) for x in line.split()[:3]]

	load = {
	'load1':  load_avgs[0],
	'load5':  load_avgs[1],
	'load15':  load_avgs[2]
	}

	#status_outp =  'Load1: ' + format( load['load1'], '.2f' ) + ' '
	#status_outp += 'Load5: ' + format( load['load5'], '.2f' ) + ' '
	#status_outp += 'Load15: ' + format( load['load15'], '.2f' )
	status_outp =  'Load1: ' + str( '%.2f' % load['load1'] ) + ' '
	status_outp += 'Load5: ' + str( '%.2f' % load['load5'] ) + ' '
	status_outp += 'Load15: ' + str( '%.2f' % load['load15'] )

	if warn is not None and crit is not None:
		status_code = 0
		for i in range( len( warn ) ):
			if crit[i] !='' and warn[i] !='':
				if float( load_avgs[i] ) >= float( crit[i] ):
					status_code = 2
					status_outp += ' (Critical)'
				elif float( load_avgs[i] ) >= float(warn[i] ):
					if status_code < 1:
						status_code = 1
					status_outp += ' (Warning)'
				else:
					status_outp += ' (OK)'
	else:
		status_code = 0

	seq=0
	for x in [ 'load1', 'load5', 'load15' ]:
		#perfdata += x + '=' + format( load[x], '.2f' )
		perfdata += x + '=' + str( '%.2f' % load[x] )
		if warn is not None and crit is not None:
			if len( warn ) >= seq+1:
				perfdata += ';' + str(warn[seq]) + ';' + str(crit[seq])
		perfdata += ' '
		seq = seq + 1
	#remove last space
	perfdata = perfdata[:-1]

	print status_outp + ' | ' + perfdata
	exit ( status_code )

def check_threads( warn=None, crit=None ):
	status_code = 3
	status_outp =''
	perfdata = ''

	#with open('/proc/loadavg') as f:
	f = open('/proc/loadavg', 'r')
	try:
		line = f.readline()
	finally:
		f.close()
	t = line.split()[3]
	threads = {
	'running': t.split('/')[0],
	'total':   t.split('/')[1]
	}

	status_outp =  'Threads: ' + t + ' '

	if warn is not None and crit is not None:
		if float( threads['running'] ) >= float( crit ):
			status_code = 2
			status_outp += ' (Critical)'
		elif float( threads['running'] ) >= float( warn ):
			status_code = 1
			status_outp += ' (Warning)'
		else:
			status_code = 0
			status_outp += ' (OK)'
	else:
		status_code = 0

	for x in [ 'running', 'total'  ]:
		#perfdata += x + '=' + format( float( threads[x] ), '.2f' )
		perfdata += x + '=' + str( '%.2f' % float( threads[x] ) )
		if warn is not None and crit is not None and x == 'running':
			perfdata += ';' + str(warn) + ';' + str(crit)
		perfdata += ' '
	#remove last space
	perfdata = perfdata[:-1]

	print status_outp + ' | ' + perfdata
	exit ( status_code )

def check_openfiles( warn=None, crit=None ):
	status_code = 3
	status_outp = ''
	perfdata = ''

	#with open('/proc/sys/fs/file-nr') as f:
	f = open('/proc/sys/fs/file-nr', 'r')
	try:
		line = f.readline()
	finally:
		f.close()
	fd = [int(x) for x in line.split()]

	ofiles = {
	'open': fd[0],
	'free': fd[1],
	'total': fd[2]
	}

	status_outp = 'Open Files: ' + str( ofiles['open'] ) + ' (free: ' + str( ofiles['free'] ) + ')'

	if warn is not None and crit is not None:
		if float( ofiles['open'] ) >= float( crit ):
			status_code = 2
			status_outp += ' (Critical)'
		elif float( ofiles['open'] ) >= float( warn ):
			status_code = 1
			status_outp += ' (Warning)'
		else:
			status_code = 0
			status_outp += ' (OK)'
	else:
		status_code = 0

	for x in [ 'open', 'free' ]:
		#perfdata += x + '=' + format( float( ofiles[x] ), '.2f' )
		perfdata += x + '=' + str( '%.2f' % float( ofiles[x] ) )
		if warn is not None and crit is not None and x == 'open':
			perfdata += ';' + str(warn) + ';' + str(crit)
			perfdata += ';0;' + str( ofiles['total'] )
		perfdata += ' '
	#remove last space
	perfdata = perfdata[:-1]

	print status_outp + ' | ' + perfdata
	exit ( status_code )


def check_procs( warn=None, crit=None ):
	status_code = 3
	status_outp =''
	perfdata = ''

	forks = 0
	#Verify if the interim file exists, if not create it now
	interim_file = INTERIM_DIR + '/' + 'proc_stat_processes'
	if not os.path.isfile( interim_file ):
		shutil.copyfile( '/proc/stat', interim_file )
		print ( 'This was the first run, run again to get values' )
		exit( 0 )
	# Get mtime of the interim file and calculate the sample period
	sample_period = float( time.time() - os.path.getmtime( interim_file ) )
	# Get the deltas proc stats interimfile - procfile(now)	
	curr_forks = 0
	for file in [ '/proc/stat', interim_file ]:
		#with open( file ) as f:
		f = open( file, 'r' )
		try:
			for line in f:
				if line.startswith( 'processes ' ):
					if file == '/proc/stat':
						curr_forks = int( line.split()[1] )
					elif file == interim_file:
						forks = curr_forks - int( line.split()[1] )	
		finally:
			f.close()
	forks_ps = float ( forks / sample_period )
	states_procs = {}
	p_total = 0
	for proc_dir in os.listdir( '/proc' ):
		if proc_dir.isdigit():
			p_total += 1
			try:
				#with open( '/proc/' + proc_dir + '/stat' ) as f:
				f = open( '/proc/' + proc_dir + '/stat', 'r' )
				try:
					line = f.readline().split()[1:3]
				finally:
					f.close()
			except:
				continue
			if line[1] not in states_procs:
				states_procs[ line[1] ] = []
			states_procs[ line[1] ].append( line[0] )
	p = {
	'total': p_total,
	'forks': forks_ps,
	'running': 0,
	'sleeping': 0,
	'waiting': 0,
	'zombie': 0,
	'others': 0
	}
	for state in states_procs:
		if state == 'R':
			p['running'] += len( states_procs[state] )
		elif state == 'S':
			p['sleeping'] += len( states_procs[state] )
		elif state == 'D':
			p['waiting'] += len( states_procs[state] )
		elif state == 'Z':
			p['zombie'] += len( states_procs[state] )
		else:
			p['others'] += len( states_procs[state] )

	status_outp += 'Total:' + str( p['total'] ) + ' Running:' + str( p['running'] ) + ' Sleeping:' + str( p['sleeping'] ) + ' Waiting:' + str( p['waiting'] )
	#status_outp += ' Zombie:' + str( p['zombie'] ) + ' Others:' + str( p['others'] ) + ' New_Forks:' + format( p['forks'], '.2f' ) + '/s'
	status_outp += ' Zombie:' + str( p['zombie'] ) + ' Others:' + str( p['others'] ) + ' New_Forks:' + str( '%.2f' % p['forks'] ) + '/s'


	if warn is not None and crit is not None:
		status_code = 0
		param = [ 'total', 'running', 'waiting' ]
		for i in range( len( warn ) ):
			if crit[i] != '' and warn[i] != '':
				if float( p[ param[i] ] ) >= float( crit[i] ):
					status_code = 2
					status_outp += ' (Critical ' + param[i] + ')'
				elif float( p[ param[i] ] ) >= float(warn[i] ):
					if ( status_code < 1 ):
						status_code = 1
					status_outp += ' (Warning ' + param[i] + ')'
				else:
					status_outp += ' (OK)'
	else:
		status_code = 0


	seq=0
	for x in [ 'total', 'forks', 'sleeping', 'running', 'waiting', 'zombie', 'others' ]:
		#perfdata += x + '=' + format( p[x], '.2f' )
		perfdata += x + '=' + str( '%.2f' % p[x] )
		if warn is not None and crit is not None:
			if x in [ 'total', 'running', 'waiting' ]:
				if len( warn ) >= seq+1:
					perfdata += ';' + str(warn[seq]) + ';' + str(crit[seq])
					seq = seq + 1
	
		perfdata += ' '
	#remove last space
	perfdata = perfdata[:-1]

	#update the interim file
	shutil.copyfile( '/proc/stat', interim_file )

	print status_outp + ' | ' + perfdata
	exit ( status_code )

def check_diskio( dev, warn=None, crit=None ):
	status_code = 3
	status_outp =''
	perfdata = ''

	#Process the device
	if dev.startswith( '/' ):
		real_path = os.path.realpath( dev )
		if str( real_path[:5] ) != '/dev/':
			print ( 'Plugin Error: Block device not found: ' + real_path + '('+device+')' )
			exit( 3 )
		else:
			device = real_path [5:]
	else:
		device = dev
	#Check if the device exist
	#with open( '/proc/diskstats' ) as f2:
	f2 = open( '/proc/diskstats', 'r' )
	try:
		proc_content = f2.read()
	finally:
		f2.close()
	sep = '%s ' % device
	found = False
	for line in proc_content.splitlines():
		if sep in line:
			found = True
			proc_line = line.strip().split(sep)[1].split()
			break
	if not found:
		print ( 'Plugin Error: Block device not found: ('+device+')' )
		exit( 3 )
	else:
		#Now the the device is found:
		#Verify if the interim file exists, if not create it now
		interim_file = INTERIM_DIR + '/' + 'proc_diskstats_' + str(device).replace( '/', '_' )
		if not os.path.isfile( interim_file ):
			shutil.copyfile( '/proc/diskstats', interim_file )
			print ( 'This was the first run, run again to get values: diskio('+device+')' )
			exit( 0 )

		# Get mtime of the interim file and calculate the sample period
		sample_period = float( time.time() - os.path.getmtime( interim_file ) )

		#with open( interim_file ) as f1:
		f1 = open( interim_file, 'r' )
		try:
			interim_content = f1.read()
		finally:
			f1.close()

		for line in interim_content.splitlines():
			if sep in line:
				interim_line = line.strip().split(sep)[1].split()
				break

		#compute deltas; refer: https://www.kernel.org/doc/Documentation/iostats.txt
		# each delta is divided by the sample period which gives us values in per second;
		d = {
			'read_operations': ( int( proc_line[0] ) - int( interim_line[0] ) ) / sample_period,
			'read_sectors':  ( int( proc_line[2] ) - int( interim_line[2] ) ) / sample_period,
			'read_time': ( int( proc_line[3] ) - int( interim_line[3] ) ) / sample_period,
			'write_operations': ( int( proc_line[4] ) - int( interim_line[4] ) ) / sample_period,
			'write_sectors': ( int( proc_line[6] ) - int( interim_line[6] ) ) / sample_period,
			'write_time': ( int( proc_line[7] ) - int( interim_line[7] ) ) / sample_period
		}

		status_outp += dev
		status_outp += '(' + device + ')'
		#status_outp += ' Read: ' + format( d['read_sectors'], '.2f' ) + ' sec/s (' + format( d['read_operations'], '.2f' ) + ' t/s)'
		#status_outp += ' Write: ' + format( d['write_sectors'], '.2f' ) + ' sec/s (' + format( d['write_operations'], '.2f' ) + ' t/s)'
		#status_outp += ' [t:' + format( sample_period, '.2f' ) + ']'
		status_outp += ' Read: ' + str( '%.2f' % d['read_sectors'] ) + ' sec/s (' + str( '%.2f' % d['read_operations'] ) + ' t/s)'
		status_outp += ' Write: ' + str( '%.2f' % d['write_sectors'] ) + ' sec/s (' + str( '%.2f' % d['write_operations'] ) + ' t/s)'
		status_outp += ' [t:' + str( '%.2f' % sample_period ) + ']'

		if warn is not None and crit is not None:
			if float( d['read_sectors'] ) >= float( crit[0] ) or float( d['write_sectors'] ) >= float( crit[1] ):
				status_code = 2
				status_outp += ' (Critical)'
			elif float( d['read_sectors'] ) >= float( warn[0] ) or float( d['write_sectors'] ) >= float( warn[1] ):
				status_code = 1
				status_outp += ' (Warning)'
			else:
				status_code = 0
				status_outp += ' (OK)'
		else:
			status_code = 0
	
		for x in [ 'read_operations', 'read_sectors', 'read_time', 'write_operations', 'write_sectors', 'write_time' ]:
			#perfdata += x + '=' + format( d[x], '.2f' ) 
			perfdata += x + '=' + str( '%.2f' % d[x] ) 
			if warn is not None and crit is not None:
				if x == 'read_sectors':
					perfdata += ';' + str(warn[0]) + ';' + str(crit[0])
				elif x == 'write_sectors':
					perfdata += ';' + str(warn[1]) + ';' + str(crit[1])
			perfdata += ' '
		#remove last space
		perfdata = perfdata[:-1]
	
		#update the interim file
		shutil.copyfile( '/proc/diskstats', interim_file )
	
		print status_outp + ' | ' + perfdata
		exit ( status_code )

def check_disku( mount, warn=None, crit=None):
	status_code = 3
	status_outp =''
	perfdata = ''

	
	if os.path.ismount( mount ):
		statvfs = os.statvfs( mount )
	else:
		print ( 'Plugin Error: Mount point not valid: (' + mount + ')' )
		exit( 3 )

	if statvfs is not None:
		du = {
		'size':  float( statvfs.f_frsize * statvfs.f_blocks / 1024.00 / 1024 / 1024 ),    # Size of filesystem
		'free':  float( statvfs.f_frsize * statvfs.f_bfree / 1024.00 / 1024 / 1024  ),    # Actual free
		'avail': float( statvfs.f_frsize * statvfs.f_bavail / 1024.00 / 1024 / 1024 )     # Available free
		}
		# Calculate Used percent
		du['used_pc'] = ( du['size'] - du['avail'] ) / du['size'] * 100

		status_outp += mount
		#status_outp += ' Used: ' + format( du['size'] - du['avail'], '.2f' ) + ' GB / ' + format( du['size'], '.2f' ) + ' GB'
		#status_outp += ' (' + format( du['used_pc'], '.2f' ) + '%)'
		status_outp += ' Used: ' + str( '%.2f' % float( du['size'] - du['avail'] ) ) + ' GB / ' + str( '%.2f' % du['size'] ) + ' GB'
		status_outp += ' (' + str( '%.2f' % du['used_pc'] ) + '%)'

		if warn is not None and crit is not None:
			if du['used_pc'] >= float( crit ):
				status_code = 2
				status_outp += ' (Critical)'
			elif du['used_pc'] >= float( warn ):
				status_code = 1
				status_outp += ' (Warning)'
			else:
				status_code = 0
				status_outp += ' (OK)'
		else:
			status_code = 0
	
		#perfdata += 'used=' + format( du['used_pc'], '.2f' ) + '%'
		perfdata += 'used=' + str( '%.2f' % du['used_pc'] ) + '%'
		if warn is not None and crit is not None:
			perfdata += ';' + str(warn) + ';' + str(crit)
	
		print status_outp + ' | ' + perfdata
		exit ( status_code )

def check_memory ( warn=None, crit=None ):
	status_code = 3
	status_outp =''
	perfdata = ''
	mem = {}
	#with open('/proc/meminfo') as f:
	f = open('/proc/meminfo', 'r')
	try:
		for line in f:
			if line.startswith( 'MemTotal: ' ):
				mem['total'] = int( line.split()[1] )
			elif line.startswith( 'Active: ' ):
				mem['active'] = int( line.split()[1] )
			elif line.startswith( 'MemFree: ' ):
				mem['free'] = int( line.split()[1] )
			elif line.startswith( 'Cached: ' ):
				mem['cached'] = int( line.split()[1] )
			elif line.startswith('Buffers: ' ):
				mem['buffers'] = int( line.split()[1] )
	finally:
		f.close()
	m = {
	'total':   float( mem['total'] / 1024.00 ),
	'active':  float( mem['active'] / 1024.00 ),
	'cached':  float( (mem['cached'] + mem['buffers']) / 1024.00 ),
	'used': float( (mem['total'] - mem['free'] - mem['cached'] - mem['buffers']) / 1024.00 ),
	'used_p': float( (mem['total'] - mem['free'] - mem['cached'] - mem['buffers']) ) / float( mem['total'] ) * 100.00
	}

	#status_outp += 'Memory Used: ' + format( m['used'], '.2f' ) + 'MB / ' + format( m['total'], '.2f' ) + 'MB (' + format( m['used_p'], '.2f' ) + '%)'
	status_outp += 'Memory Used: ' + str( '%.2f' % m['used'] ) + 'MB / ' + str( '%.2f' % m['total'] ) + 'MB (' + str( '%.2f' % m['used_p'] ) + '%)'

	if warn is not None and crit is not None:
		if m['used_p'] >= float( crit ):
			status_code = 2
			status_outp += ' (Critical)'
		elif m['used_p'] >= float( warn ):
			status_code = 1
			status_outp += ' (Warning)'
		else:
			status_code = 0
			status_outp += ' (OK)'
	else:
		status_code = 0

	for x in [ 'used', 'cached', 'active' ]:
		#perfdata += x + '=' + format( m[x], '.2f' )
		perfdata += x + '=' + str( '%.2f' % m[x] )
		if x == 'used':
			if warn is not None and crit is not None:
				warn_mb = int( m['total'] * float( warn ) / 100 )
				crit_mb = int( m['total'] * float( crit ) / 100 )
				perfdata += ';' + str( warn_mb ) + ';' + str( crit_mb )
			else:
				perfdata += ';;'
			perfdata += ';0;' + str( int( m['total'] ) )
		perfdata += ' '
	#remove last space
	perfdata = perfdata[:-1]

	print status_outp + ' | ' + perfdata
	exit ( status_code )
def check_swap ( warn=None, crit=None ):
	status_code = 3
	status_outp =''
	perfdata = ''
	swap = {}
	#with open('/proc/meminfo') as f:
	f = open('/proc/meminfo', 'r')
	try:
		for line in f:
			if line.startswith('SwapTotal: ' ):
				swap['total'] = int( line.split()[1] )
			elif line.startswith('SwapFree: ' ):
				swap['free'] = int( line.split()[1] )
			elif line.startswith('SwapCached: ' ):
				swap['cached'] = int( line.split()[1] )
	finally:
		f.close()
	s = {
	'total':   float( swap['total'] / 1024.00 ),
	'cached':  float( swap['cached'] / 1024.00 ),
	'used':    float( (swap['total'] - swap['free'] - swap['cached']) / 1024.00 ),
	'used_p':  float( swap['total'] - swap['free'] - swap['cached'] ) / swap['total'] * 100.00
	}

	#status_outp += 'Swap Used: ' + format( s['used'], '.2f' ) + 'MB / ' + format( s['total'], '.2f' ) + 'MB (' + format( s['used_p'], '.2f' ) + '%)'
	status_outp += 'Swap Used: ' + str( '%.2f' % s['used'] ) + 'MB / ' + str( '%.2f' % s['total'] ) + 'MB (' + str( '%.2f' % s['used_p'] ) + '%)'

	if warn is not None and crit is not None:
		if s['used_p'] >= float( crit ):
			status_code = 2
			status_outp += ' (Critical)'
		elif s['used_p'] >= float( warn ):
			status_code = 1
			status_outp += ' (Warning)'
		else:
			status_code = 0
			status_outp += ' (OK)'
	else:
		status_code = 0
	for x in [ 'used', 'cached' ]:
		#perfdata += x + '=' + format( s[x], '.2f' )
		perfdata += x + '=' + str( '%.2f' % s[x] )
		if x == 'used':
			if warn is not None and crit is not None:
				warn_mb = int( s['total'] * float( warn ) / 100 )
				crit_mb = int( s['total'] * float( crit ) / 100 )
				perfdata += ';' + str( warn_mb ) + ';' + str( crit_mb )
			else:
				perfdata += ';;'
			perfdata += ';0;' + str( int( s['total'] ) )
		perfdata += ' '
	#remove last space
	perfdata = perfdata[:-1]

	print status_outp + ' | ' + perfdata
	exit ( status_code )

def check_net ( interface, warn=None, crit=None ):
	status_code = 0
	status_outp =''
	perfdata = ''

	#Verify if the interim file exists, if not create it now
	interim_file = INTERIM_DIR + '/' + 'proc_net_dev_' + interface
	if not os.path.isfile( interim_file ):
		shutil.copyfile( '/proc/net/dev', interim_file )
		print ( 'This was the first run, run again to get values: net:' + interface )
		exit( 0 )

	# Get mtime of the interim file and calculate the sample period
	sample_period = float ( time.time() - os.path.getmtime( interim_file ) )

	# Calculate the deltas
	int_t = {}
	int_d = {}
	for file in ['/proc/net/dev', interim_file]:
		#with open( file ) as f:
		f = open( file, 'r' )
		try:
			for line in f:
				line = line.strip()
				if line.startswith( interface+':' ):
					seq = 0
					for x in ['r_bytes','r_packets','r_errs','r_drop','r_fifo','r_frame','r_compressed','r_multicast',
						't_bytes','t_packets','t_errs','t_drop','t_fifo','t_colls','t_carrier','t_compressed']:
						# if files is current/proc, load values in int_t
						if file == '/proc/net/dev':
							int_t[x] = int( line.split( interface+':' )[1].split()[seq] )
						# if file is interim calculate the diff and load deltas in int_d
						elif file == interim_file:
							interim_value = int( line.split( interface+':' )[1].split()[seq] )
							int_d[x] = int_t[x] - interim_value
						seq += 1
					break
		finally:
			f.close()
	if not int_t or not int_d:
		#interface not found
		print ( 'Plugin Error: Network device not found: ('+interface+')' )
		exit( 3 )
	else:
		int_d['RX_MBps'] = float( int_d['r_bytes'] / 1024.00 / 1024.00 / sample_period )
		int_d['TX_MBps'] = float( int_d['t_bytes'] / 1024.00 / 1024.00 / sample_period )
		int_d['RX_PKps'] = float( int_d['r_packets'] / sample_period )
		int_d['TX_PKps'] = float( int_d['t_packets'] / sample_period )

		status_outp += interface
		#status_outp += ' Rx: ' + format( int_d['RX_MBps'], '.2f' ) + ' MB/s (' + format( int_d['RX_PKps'], '.2f' ) + ' p/s)'
		#status_outp += ' Tx: ' + format( int_d['TX_MBps'], '.2f' ) + ' MB/s (' + format( int_d['TX_PKps'], '.2f' ) + ' p/s)'
		#status_outp += ' [t:' + format( sample_period, '.2f' ) + ']'
		status_outp += ' Rx: ' + str( '%.2f' % int_d['RX_MBps'] ) + ' MB/s (' + str( '%.2f' % int_d['RX_PKps'] ) + ' p/s)'
		status_outp += ' Tx: ' + str( '%.2f' % int_d['TX_MBps'] ) + ' MB/s (' + str( '%.2f' % int_d['TX_PKps'] ) + ' p/s)'
		status_outp += ' [t:' + str( '%.2f' % sample_period ) + ']'

		# Check packet errors
		int_d['PK_ERRORS'] = 0
		for x in ['r_errs','r_drop','r_fifo','r_frame',
			't_errs','t_drop','t_fifo','t_colls','t_carrier']:
			if float( int_d[x] ) > 0:
				int_d['PK_ERRORS'] += int_d[x]
				status_code = 2
				status_outp += ' (Critical ' + x + ':' + str(int_d[x]) + ')'
		# Skip bw checks if packer error
		if warn is not None and crit is not None and int_d['PK_ERRORS'] == 0:
			if float( int_d['RX_MBps'] ) >= float( crit[0] ) or float( int_d['TX_MBps'] ) >= float( crit[1] ):
				status_code = 2
				status_outp += ' (Critical BW)'
			elif float( int_d['RX_MBps'] ) >= float( warn[0] ) or float( int_d['TX_MBps'] ) >= float( warn[1] ):
				if status_code < 1:
					status_code = 1
				status_outp += ' (Warning BW)'
			else:
				status_outp += ' (OK)'

		for x in [ 'RX_MBps', 'RX_PKps', 'TX_MBps', 'TX_PKps', 'PK_ERRORS']:
			#perfdata += x + '=' + format( int_d[x], '.2f' ) 
			perfdata += x + '=' + str( '%.2f' % int_d[x] ) 
			if warn is not None and crit is not None :
				if x == 'RX_MBps':
					perfdata += ';' + str(warn[0]) + ';' + str(crit[0])
				elif x == 'TX_MBps':
					perfdata += ';' + str(warn[1]) + ';' + str(crit[1])
			perfdata += ' '
		#remove last space
		perfdata = perfdata[:-1]

		#update the interim file
		shutil.copyfile( '/proc/net/dev', interim_file )

		print status_outp + ' | ' + perfdata
		exit ( status_code )

if __name__ == '__main__':

	if len( sys.argv ) > 1:
		# cpu warn crit sample
		if sys.argv[1] == 'cpu':
			# no arg passed after cpu
			if len( sys.argv ) == 2:
				check_cpu()
			# 2 args passed after cpu; warn,crit
			elif len( sys.argv ) == 4:
				if float( sys.argv[3] ) > float( sys.argv[2] ):
					check_cpu( warn=sys.argv[2], crit=sys.argv[3] )
				else:
					print ( 'Plugin Error: Warning('+sys.argv[2]+') threshold should be less than critical('+sys.argv[3]+')' )
					exit ( 3 )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
	
		# procs
		elif sys.argv[1] == 'procs':
			# no arg passed after procs
			if len( sys.argv ) == 2:
				check_procs()
			# if 2 args passed after procs
			elif len( sys.argv ) == 4:
				#process comma separated arguments
				warn_arr = sys.argv[2].split(',')
				crit_arr = sys.argv[3].split(',')
				if len(warn_arr) > 3 or len(warn_arr) < 1 or len(warn_arr) != len(crit_arr):
					print ( 'Plugin Error: Invalide arguments for load: ('+str(sys.argv)+')' )
					exit( 3 )
				else:
					for i in range( len( warn_arr ) ):
						if warn_arr[i] != '' and crit_arr[i] != '':
							if float(warn_arr[i]) > float(crit_arr[i]):
								print ( 'Plugin Error: Warning('+warn_arr[i]+') threshold should be less than critical('+crit_arr[i]+')' )
								exit( 3 )
					check_procs( warn=warn_arr, crit=crit_arr )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
				
		# load
		elif sys.argv[1] == 'load':
			# no arg passed after load
			if len( sys.argv ) == 2:
				check_load()
			# if 2 args passed after load
			elif len( sys.argv ) == 4:
				#process comma separated arguments
				warn_arr = sys.argv[2].split(',')
				crit_arr = sys.argv[3].split(',')
				if len(warn_arr) > 3 or len(warn_arr) < 1 or len(warn_arr) != len(crit_arr):
					print ( 'Plugin Error: Invalide arguments for load: ('+str(sys.argv)+')' )
					exit( 3 )
				else:
					for i in range( len( warn_arr ) ):
						if warn_arr[i] != '' and crit_arr[i] != '':
							if float(warn_arr[i]) > float(crit_arr[i]):
								print ( 'Plugin Error: Warning('+warn_arr[i]+') threshold should be less than critical('+crit_arr[i]+')' )
								exit( 3 )
					check_load( warn=warn_arr, crit=crit_arr )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
		# threads
		elif sys.argv[1] == 'threads':
			# no arg passed after procs
			if len( sys.argv ) == 2:
				check_threads()
			# if 2 args passed after procs
			elif len( sys.argv ) == 4:
				if float( sys.argv[3] ) > float( sys.argv[2] ):
					check_threads( warn=sys.argv[2], crit=sys.argv[3] )
				else:
					print ( 'Plugin Error: Warning('+sys.argv[2]+') threshold should be less than critical('+sys.argv[3]+')' )
					exit( 3 )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
				
		# Open files
		elif sys.argv[1] == 'files':
			# no arg passed after procs
			if len( sys.argv ) == 2:
				check_openfiles()
			# if 2 args passed after procs
			elif len( sys.argv ) == 4:
				if float( sys.argv[3] ) > float( sys.argv[2] ):
					check_openfiles( warn=sys.argv[2], crit=sys.argv[3] )
				else:
					print ( 'Plugin Error: Warning('+sys.argv[2]+') threshold should be less than critical('+sys.argv[3]+')' )
					exit( 3 )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
		# diskio dev warn(read,write) crit(read,write)
		elif sys.argv[1] == 'diskio':
			# no arg passed after diskio [dev]
			if len( sys.argv ) == 3:
				check_diskio( sys.argv[2] )
			# if 2 args passed after diskio [dev]
			elif len( sys.argv ) == 5:
				#process comma separated arguments
				#we convert it to an array and pass it on
				warn_arr = sys.argv[3].split(',')
				crit_arr = sys.argv[4].split(',')
				if len(warn_arr) != 2 or len(warn_arr) != len(crit_arr):
					print ( 'Plugin Error: Invalide arguments for ' + sys.argv[1] + ': ('+str(sys.argv)+')' )
					exit( 3 )
				else:
					for i in range( len( warn_arr ) ):
						if float(warn_arr[i]) > float(crit_arr[i]):
							print ( 'Plugin Error: Warning('+warn_arr[i]+') threshold should be less than critical('+crit_arr[i]+')' )
							exit( 3 )
					check_diskio( sys.argv[2], warn=warn_arr, crit=crit_arr )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
		# disku mount warn crit
		elif sys.argv[1] == 'disku':
			# no arg passed after disku mount
			if len( sys.argv ) == 3:
				check_disku( sys.argv[2] )
			# if 2 args passed after disku mount
			elif len( sys.argv ) == 5:
				if float( sys.argv[4] ) > float ( sys.argv[3] ):
					check_disku( sys.argv[2] , warn=sys.argv[3], crit=sys.argv[4] )
				else:
					print ( 'Plugin Error: Warning('+sys.argv[2]+') threshold should be less than critical('+sys.argv[3]+')' )
					exit( 3 )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
		# memory warn crit
		elif sys.argv[1] == 'memory':
			# no arg passed after memory
			if len( sys.argv ) == 2:
				check_memory()
			# if 2 args passed after memory
			elif len( sys.argv ) == 4:
				if float( sys.argv[3] ) > float( sys.argv[2] ):
					check_memory( warn=sys.argv[2] , crit=sys.argv[3] )
				else:
					print ( 'Plugin Error: Warning('+sys.argv[2]+') threshold should be less than critical('+sys.argv[3]+')' )
					exit( 3 )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
		# swap warn crit
		elif sys.argv[1] == 'swap':
			# no arg passed after swap
			if len( sys.argv ) == 2:
				check_swap()
			# if 2 args passed after swap
			elif len( sys.argv ) == 4:
				if float( sys.argv[3] ) > float( sys.argv[2] ):
					check_swap( warn=sys.argv[2] , crit=sys.argv[3] )
				else:
					print ( 'Plugin Error: Warning('+sys.argv[2]+') threshold should be less than critical('+sys.argv[3]+')' )
					exit( 3 )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
	
		# network iface warn(rx,tx)  crit(rx,tx)
		elif sys.argv[1] == 'network':
			# no arg passed after network iface
			if len( sys.argv ) == 3:
				check_net( sys.argv[2] )
			# if 2 args passed after network iface
			elif len( sys.argv ) == 5:
				#process comma separated arguments
				#we convert it to an array and pass it on
				warn_arr = sys.argv[3].split(',')
				crit_arr = sys.argv[4].split(',')
				if len(warn_arr) != 2 or len(warn_arr) != len(crit_arr):
					print ( 'Plugin Error: Invalide arguments for ' + sys.argv[1] + ': ('+str(sys.argv)+')' )
					exit( 3 )
				else:
					for i in range( len( warn_arr ) ):
						if float(warn_arr[i]) > float(crit_arr[i]):
							print ( 'Plugin Error: Warning('+warn_arr[i]+') threshold should be less than critical('+crit_arr[i]+')' )
							exit( 3 )
					check_net( sys.argv[2], warn=warn_arr, crit=crit_arr )
			else:
				print ( 'Plugin Error: Invalide arguments for '+sys.argv[1]+': ('+str(sys.argv)+')' )
				exit( 3 )
		else:
			print ( 'What?' )
			exit( 3 )
		
