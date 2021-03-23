global NodeIP
NodeIP ="111.111.111.111"
global wei
wei = 1000000000000000000
global filename
filename = 'wallets_list.txt'

def dump_wallets(fname,wlist):
 wfile = open(fname,"wt") 
 wfile.write('wallet:                              balance: '+chr(13))
 wfile.close()	
 wfile = open(fname,"at")
 for z in range (0,len(wlist)):
  one_w = str(wlist[z][0]+' '+str(wlist[z][1])+chr(13))
  wfile.write(one_w)
 wfile.close()
 print(str(z+1)+' wallets saved to the file '+fname)
