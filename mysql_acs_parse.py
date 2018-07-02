#!/usr/bin/env python3.6

import socket
import json
from datetime import datetime, timedelta



t1 = datetime.now()
td = timedelta(seconds=300)
#print(datetime.strftime(t1, "%Y-%m-%d-%H-%M-%S"))
req_date = datetime.strftime((t1 - td), "%Y-%m-%d-%H-%M-%S")

sql_db = {
         "statperio":"select count(*) from hostoptions where name = 'statperio20180614' and int_val > '0'", 
         "statbcast":"select count(*) from hostoptions where name = 'statbcast20180614' and int_val > '0'",
         "lastcontact": "select p.name, p.description, h.serial, i.lastcontact, i.url "
            "from hostsbean h left join deviceprofilebean p on (h.pfid = p.id) left join hostinfobean i on h.id = i.hst_id "
            "where i.lastcontact < '" + req_date + "' order by i.lastcontact",
}

def getMysql(sql_h=None, sql_b=None):
   if sql_b != None:
      global sql1
      sql_b = sql_db[sql_b]
      data = [sql_h, sql_b]
      data = json.dumps(data)
      out = []
      with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
         sock.sendto(bytes(data, 'utf-8'), ('10.10.1.5',40069))
         while True:
            resp, addr = sock.recvfrom(1024)
            resp = resp.decode('utf-8')
            if resp == "END":
               break
            else:
               out.append(resp)
         return out
   else:
      return ["None"]



if __name__ == '__main__':
   test_date = "2018-06-16-12-50"
   test = {
   "lastcontact": "select h.pfid, p.name, p.description, h.serial, i.lastcontact, i.url "
                  "from hostsbean h left join deviceprofilebean p on (h.pfid = p.id) left join hostinfobean i on h.id = i.hst_id "
                  "where i.lastcontact < '" + test_date + "' order by h.pfid"
   }
   t1 = datetime.now()
   td = timedelta(seconds=300)
   print(datetime.strftime(t1, "%Y-%m-%d-%H-%M-%S"))
   print(datetime.strftime((t1 - td), "%Y-%m-%d-%H-%M-%S"))
