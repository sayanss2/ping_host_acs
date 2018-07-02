#!/usr/bin/env python3.6
"""
REQUIREMENTS
	qt5-default
	sshpass
	fping



fping
Output options:
   -a, --alive        show targets that are alive
   -A, --addr         show targets by address
   -C, --vcount=N     same as -c, report results in verbose format
   -D, --timestamp    print timestamp before each output line
   -e, --elapsed      show elapsed time on return packets
   -i, --interval=MSEC  interval between sending ping packets (default: 10 ms)
   -n, --name         show targets by name (-d is equivalent)
   -N, --netdata      output compatible for netdata (-l -Q are required)
   -o, --outage       show the accumulated outage time (lost packets * packet interval)
   -q, --quiet        quiet (don't show per-target/per-ping results)
   -Q, --squiet=SECS  same as -q, but show summary every n seconds
   -s, --stats        print final stats
   -u, --unreach      show targets that are unreachable
   -v, --version      show version
"""

import subprocess
import sys
import re
from multiprocessing import Process, Queue
import mysql_acs_parse



argv = sys.argv
fping_action = "-a"
ssh_known_hosts_url = "/home/sonic/.ssh/known_hosts"
sshgen_url = "/home/sonic/_work_eltex/logs/ems/PSSWDGenCon"

func_case = {
	'--reboot': "reboot",
	'--killtr': "killall -9 org.eltex.tr69",
	'--mquery': 0,
	'-l': None,
	'--mysql': 0,
	}



def ping_h(fping_action, ip, sn, sshgen_url, ssh_known_hosts_url, *args):
	with subprocess.Popen(["fping", fping_action, ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
		out, err = proc.communicate()
		line_p = out.decode().strip('\n')
		if line_p != '':
			with subprocess.Popen([sshgen_url, "--sn", sn, "--user", "root"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
				out, err = proc.communicate()
				line_key = out.decode().strip('\n')
				print(sn + ':' + line_p + ':' + line_key)
				#print(line_p + ':' + sn)
				if func_case[args[1]] != None:
					print(func_case[args[1]])
					with open(ssh_known_hosts_url, 'w') as f:
						f.write("")
					with subprocess.Popen(["sshpass", "-p", line_key, "ssh", "-oStrictHostKeyChecking=no", "root@"+line_p, func_case[args[1]],], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
						pass



def list_f(input_file):
	try:
		with open(input_file) as f:
			ip_list = []
			sn_list = []
			for i in f:
				line = i.strip('\n')
				ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
				sn = re.findall( r'^.{10,10}', line )
				try:
					ip_list.append(ip[0])
					sn_list.append(sn[0])
				except IndexError:
#					ip_list.append('127.0.0.1')
					pass
			return (ip_list, sn_list)
	except:
		print("File [" + input_file +"] not found")
		#sys.exit()



def list_m(sql_req, parse_arg=None):
	my = mysql_acs_parse.getMysql(sql_b=sql_req)
	ip_list = []
	sn_list = []
	for line in my:
		if parse_arg != None:
			if re.search(parse_arg, line):
				ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
				sn = re.findall( r'SB+.{8,8}', line )
				try:
					ip_list.append(ip[0])
					sn_list.append(sn[0])	
				except IndexError:
					pass
		else:
			ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
			sn = re.findall( r'SB+.{8,8}', line )
			try:
				ip_list.append(ip[0])
				sn_list.append(sn[0])	
			except IndexError:
				pass
	return (ip_list, sn_list)



if __name__ == '__main__':
	try:
		if (argv[1] == "--mquery") and (len(argv) == 3):
			my = mysql_acs_parse.getMysql(sql_b=argv[2])
			for line in my:
				print(line)
			sys.exit()
		elif ((func_case[argv[1]] != 0) and (len(argv) == 3)) and (argv[2] != "--mysql"):
			try:
				ip_list, sn_list = list_f(argv[2])
				for ip, sn in zip(ip_list, sn_list):
					p1 = Process(target=ping_h, args=(fping_action, ip, sn, sshgen_url, ssh_known_hosts_url, *argv,))
					p1.start()
			except:
				sys.exit()
		elif ((func_case[argv[1]] != 0) and (len(argv) >= 3)) and (argv[2] == "--mysql"):
			try:
				filter = None
				if len(argv) >= 4:
					filter = argv[3]
				ip_list, sn_list = list_m("lastcontact", parse_arg=filter)
				for ip, sn in zip(ip_list, sn_list):
					p1 = Process(target=ping_h, args=(fping_action, ip, sn, sshgen_url, ssh_known_hosts_url, *argv,))
					p1.start()
			except:
				sys.exit()
		else:
			raise(KeyError)
	except (KeyError, IndexError):
		print("""
./ping_host.py [options] [targets...]

Output options:
	-l 	 [options] 	-list of access STB
	--killtr [options]	-remote close TR69 on STB
   	--reboot [options]	-remote reboot STB
		[FILEPATH]	-path to file export fron EMS
		--mysql	-get statistic from acs over mysql

   	--mquery [options]	-get statistic from acs over mysql
   		lastcontact	-list of access STB
   		statperio
   		statbcast
			"""
			)