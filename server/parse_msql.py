#!/usr/bin/env python3

import socket
import mysql.connector
import json



def main():
   cnx = mysql.connector.connect(user='acs', password='acsacs',
      host='127.0.0.1', 
      database='')
   cursor = cnx.cursor()
   query = ("SHOW DATABASES")
   cursor.execute(query,)
   for line in cursor:
      print(line)
   cursor.close()
   cnx.close()



def query_tomysql(head_q, query):
   cnx = mysql.connector.connect(user='acs', password='acsacs',
      host='127.0.0.1',
      database='acsmain')
   cursor = cnx.cursor()
   cursor.execute(query)
   out = []
   for line in cursor:
         #print(line)
         out.append(line)
   cursor.close()
   cnx.close()
   return out



if __name__ == '__main__':
   with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      sock.bind(('0.0.0.0', 40069))
      #main()
      while True:
         req, addr = sock.recvfrom(1024)
         if req:
            req = req.decode('utf-8')
            req = json.loads(req)
            head_q, query = req
            #print(query + "\n" + head_q)
            #resp = []
            resp = query_tomysql(head_q, query)
            for i in resp:
               sock.sendto(str(i).encode('utf-8'), addr)
            sock.sendto("END".encode('utf-8'), addr)
            #print(json.dumps(resp))
            #print(query_tomysql(head_q, query))
            #sock.sendto(bytes(json.dumps(resp, sort_keys=True, indent=4), 'utf-8'), addr)
         pass
