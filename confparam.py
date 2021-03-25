import json
import os

global NodeIP
NodeIP = "xxx.xxx.xxx.xxx"

global filename
filename = 'wallets_list.json'
global wei
wei = 1000000000000000000
global DEBUG
DEBUG = True
global kbdstop          #Stop by keyboard 
kbdstop = False        #Pauses execution after each subchains handled, if True

global maxchains        #Stop after this number of subchains handled
maxchains = 1550       # Set 0 to switch off

global continuemode      #False - start from the genesis block, 
continuemode = False     #True - to continue from a wallet saved in hls_latest

def dump_wallets(fname,wlist):
 wdump	= json.dumps(wlist)
 fdump = {
          'wallets': wdump
         }
 with open(fname,"w") as wfile:
  json.dump(fdump,wfile)
 wfile.close()
 print(str(len(wlist))+' wallets saved to the file '+fname)

def latest_dump(lwallet):
 wfile = open("hls_latest","wt")
 wfile.write(lwallet)
 wfile.close()


def dump_astext(fname,wlist):
 wfile = open(fname,"wt") 
 wfile.write('wallet:                              balance: '+chr(13))
 wfile.close()	
 wfile = open(fname,"at")
 for z in range (0,len(wlist)):
  one_w = str(wlist[z][0]+' '+str(wlist[z][1])+chr(13))
  wfile.write(one_w)
 wfile.close()


def read_last():
 try:
  wfile = open("hls_latest","rt")	
  lwallet = wfile.read()
  wfile.close()
 except:
  print('There is no any latest wallet saved ') 
 return lwallet 
  
def read_wallets(fname):
 try:
  with open(fname,"r") as wfile:
   wlist = json.load(wfile)
  wfile.close()
 except:
  wlist = None	
  print('There is no any wallets file saved ') 
 return json.loads(wlist['wallets']) 
 
 
  