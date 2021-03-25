#!/usr/bin/env python

import os
import time
import json
import random
import requests
import websocket
from websocket import create_connection
import binascii
import datetime
from datetime import datetime
import codecs
#Config parameters
from confparam import NodeIP
from confparam import wei
from confparam import DEBUG
from confparam import maxchains
from confparam import kbdstop
from confparam import continuemode
from confparam import filename
from confparam import dump_wallets
from confparam import latest_dump
from confparam import read_wallets
from confparam import read_last

#Variables: 
global server
global error
global ws
error = [None] * 5

wallets = []
balances = []
error_wallets = []

#Genesis address
addr1 = b'k\xfa\xf9\x95\xff\xce{\xe6\xe3\x07=\xc8\xaa\xf4^D\\\xf24\xe2'
genesis = '0x'+str(addr1.hex())

#print(addr1.hex())
#print(genesis)
#addr_b = bytes.fromhex(genesis[2:])
#print(addr_b)
#print(addr1)

def id_rnd():
    idr= random.randint(1,100000000) 
    idr= '"id":'+str(idr)
    return idr

def ws_con():
 global ws
 try:
  ws = create_connection(server)
  error[0] = None
 except:
  error[0] = "Unable to connect to " + server

def node_ok():
 ws.send('{"jsonrpc": "2.0", "method": "hls_ping", "params": [],'+id_rnd()+'}')
 result =  ws.recv()
 pingnode = json.loads(result)
 print('Node connected?:  '+str(pingnode["result"]))

#Connect to node
myserver = "ws://" + NodeIP
serverport = "30304"
server = myserver+":"+serverport
ws_con()
node_ok()

#' + '"' + addr + '"' + '
#' + '"' + blockno + '"' + '

def addr_bal(addr):
 ws.send('{"jsonrpc": "2.0", "method":"hls_getBalance", "params":[' + '"' + addr + '"' + ',"latest"],'+id_rnd()+'}')
 result =  ws.recv() 
 blockbal = json.loads(result)
 return blockbal['result']

def get_bals():
 total_bal = 0	
 for x in range (0,len(wallets)):
  item_addr = wallets[x]	
  item_bal = int(addr_bal(item_addr),0)/wei  
  item = [item_addr,item_bal]
  balances.append(item)
  total_bal = total_bal + item_bal
  if DEBUG:
  	print('wallet '+str(item_addr)+" balance:   "+str(item_bal))
 if DEBUG:
  print(str(len(wallets))+' wallets, total balance:   '+str(total_bal))
 return total_bal 
    
#bal = addr_bal(genesis)
#if DEBUG:
# print(str(genesis)+' balance: '+str(int(bal,0)/wei))

def latest_block(addr):
 ws.send('{"jsonrpc": "2.0", "method":"hls_getBlockNumber", "params":[' + '"' + addr + '"' + ',"latest"],'+id_rnd()+'}')
 result1 =  ws.recv() 
 lblock = json.loads(result1)
 return lblock['result']

def outtx_num(addr):
 ws.send('{"jsonrpc": "2.0", "method":"hls_getTransactionCount", "params":[' + '"' + addr + '"' + ',"latest"],'+id_rnd()+'}')
 result1 =  ws.recv() 
 txcount = json.loads(result1)
 try:
  tx_num = txcount['result']
 except: 
  tx_num = '0x0'
  err_item = [addr,txcount['error']]
  error_wallets.append(err_item)
 return tx_num


def get1block(num, addr):
 ws.send('{"jsonrpc": "2.0", "method":"hls_getBlockByNumber", "params":[' + '"' + num + '"' + ',' + '"' + addr + '"' + ',true],'+id_rnd()+'}')
 result =  ws.recv() 
 block1 = json.loads(result)
 return block1['result']

def blocktx(z,chainaddr):
 count_found = 0	
 block = get1block(z,chainaddr)
 if DEBUG:
  print('Getting '+str(len(block['transactions']))+' sent tx in block '+str(block['number']))
 if len(block['transactions']) != 0:
  count_found = count_found + len(block['transactions'])
  for x in range (0,len(block['transactions'])):
   wallet = block['transactions'][x]['to']	
   if wallet not in wallets:
    wallets.append(wallet)	#add new wallets if found
   if DEBUG:
    print('New wallet sent_to found: ')
    print(x)	
    print(block['transactions'][x]['to'])
 return count_found         

#Build wallets list

if continuemode:          #Start processing from the latest done if True, set in confparam
 
 wallets = []
 balances = read_wallets(filename)
 print(str(len(balances))+' items loaded')
 for s in range (0,len(balances)):
  wallets.append(balances[s][0])
 print(str(len(wallets))+' wallets now')
 balances = []
 chain = read_last()
 pp = wallets.index(chain)
 print('The last processed chain was #'+str(pp)+' : '+chain) 
 pp = pp + 1
 chain = wallets[pp]
 print('The next chain is #'+str(pp)+' : '+chain)
# print(wallets)
 input('continue  ?')
 work = True
 
else:	                    #Start processing from the beginning if False
 wallets.append(genesis)  #First add genesis subchain to the list:
 chain = wallets[0]       
 work = True

#LOOP until the list ends

while work:     
 print(str(chain)+' subchain is processing')
 counttx = outtx_num(chain)    # Get a number of send tx in this subchain
 print('There are '+str(int(counttx,0))+' sent tx in this chain. Continue?')
 
 if int(counttx,0) > 0:           #PASS if there are no outcoming tx
  blockno = latest_block(chain)   #Get blocks number of subchain:
  if DEBUG:
   print(str(chain)+' contains '+str(int(blockno,0))+' blocks')
  
  z = '0x1'          #Processing all blocks in each subchain, start from the 2nd, ie 0x1
  found_tx = 0                  
  y = 1
  while y <= int(blockno,0) and found_tx < int(counttx,0): 
#   if DEBUG:
#    print('Processing block '+str(z)+' of subchain '+str(chain))
#    print('estimated tx num: '+str(int(counttx,0))+' done: '+str(found_tx)+' y count: '+str(y))

   found_tx = found_tx + blocktx(z,chain)
   if found_tx < int(counttx,0):  #continue to next block if found tx less than estimated
    z=hex(int(z,0)+1)
    y = y + 1
 pp = wallets.index(chain)      
 if DEBUG:
#  print(wallets)
  print('chain No. '+str(pp)+' '+str(chain)+' done')
  print('Now wallets list contains '+str(len(wallets))+' items ')
  
 
 if pp == len(wallets):          #STOP if the last processed / Normal STOP
  work = False
  supply = get_bals()
  dump_wallets(filename,balances)
  print('Total HLS:  '+str(supply))
 else:                           #go to the next subchain
  pp = pp + 1
  chain = wallets[pp] 

 if maxchains > 0:         #STOP if maxchains defined. Set value > 0 in confparam to activate
  if pp > maxchains:                  
   work = False
   supply = get_bals()
   dump_wallets(filename,balances)
   latest_dump(wallets[pp-1])
   print('Total HLS:  '+str(supply)) 
 
 if kbdstop:              #STOP by keyboard after each subchain. Set True in confparam to activate
  manualstop = ""
  manualstop = input('Next chain?') 
  if manualstop == "n":
   work = False
   supply = get_bals()
   dump_wallets(filename,balances)
   latest_dump(wallets[pp-1])
   print('Total HLS:  '+str(supply))    
  
print('There are '+str(len(error_wallets))+' errors: ')   # report Errors  detected
for e in range (0,len(error_wallets)):
 print(str(error_wallets[e][0])+'  '+str(error_wallets[e][1]))
if len(error_wallets) == 0:
 print('No errors detected')

# Test shit, don't care:
"""
 if node_ok():
  pp = pp + 1
  chain = wallets[pp]
 else:
  work = False
  print('Connection failed...')
""" 
# sleep(5)



