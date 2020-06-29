import rsa
import hashlib
import binascii
from datetime import datetime
import numpy as np
import sys
import os


#following method is from provided sample.py file
# gets the hash of a file; from https://stackoverflow.com/a/44873382
def hashFile(filename):
    h = hashlib.sha256()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()

#following method is from provided sample.py file
# given an array of bytes, return a hex reprenstation of it
def bytesToString(data):
    return binascii.hexlify(data)

#following method is from provided sample.py file
# given a hex reprensetation, convert it to an array of bytes
def stringToBytes(hexstr):
    return binascii.a2b_hex(hexstr)

#following method is from provided sample.py file
# Load the wallet keys from a filename
def loadWallet(filename):
    with open(filename, mode='rb') as file:
        keydata = file.read()
    privkey = rsa.PrivateKey.load_pkcs1(keydata)
    pubkey = rsa.PublicKey.load_pkcs1(keydata)
    return pubkey, privkey

#get the wallet tag (first 16 of hash of pubkey)
def getWalletTag(filename):
    return (hashlib.sha256(loadWallet(filename)[0].save_pkcs1(format='PEM'))).hexdigest()[:16]

#count number of block files
def countBlocks():
    blocknum = 0
    while os.path.exists('block_' + str(blocknum) + '.txt'):
        blocknum+=1
    return blocknum


#following method is from provided sample.py file
# save the wallet to a file
def saveWallet(pubkey, privkey, filename):
    # Save the keys to a key format (outputs bytes)
    pubkeyBytes = pubkey.save_pkcs1(format='PEM')
    privkeyBytes = privkey.save_pkcs1(format='PEM')
    # Convert those bytes to strings to write to a file (gibberish, but a string...)
    pubkeyString = pubkeyBytes.decode('ascii')
    privkeyString = privkeyBytes.decode('ascii')
    # Write both keys to the wallet file
    with open(filename, 'w') as file:
        file.write(pubkeyString)
        file.write(privkeyString)
    return

def parseRecord(transaction):
    words = transaction.split(' ')
    src = words[0]
    amount = words[2]
    dest = words[4]
    return src, amount, dest


"""
Print the name of the cryptocurrency (name). 
This is the name from the Overview section, above. 
There are no additional command line parameters to this function.
"""
def name():
    print("MattCoin")
    return


"""
Create the genesis block (genesis): this is the initial block in the block chain, 
and the block should always be the same. Come up with a fun quote! 
It should be written to a block_0.txt file. 
There are no additional command line parameters to this function.
"""
def genesis():
    blockFile = open('block_0.txt', 'w')
    print('Numero Uno \n\n', file = blockFile)
    print('Genesis block created in \'block_0.txt\'')
    blockFile.close()
    return


"""
Generate a wallet (generate): this will create RSA public/private key set 
(1024 bit keys is appropriate for this assignment). 
The resulting wallet file MUST BE TEXT -- 
you will have to convert any binary data to text to save it 
(and convert it in the other direction when loading). 
You can see the provided helper functions, above, to help with this. 
The file name to save the wallet to will be provided as an additional command line parameter.
"""
def generate(walletName):
    walletFile = open(walletName, 'w')
    walletFile.close()
    pubkey, privkey = rsa.newkeys(1028)
    saveWallet(pubkey, privkey, walletName)
    print('New wallet generated in ' + walletName + ' with signature ' + getWalletTag(walletName))
    return

"""
Get wallet tag (address): this will print out the tag the public key for a given wallet, 
which is likely the hash of the public key. Note that it only prints out that tag (no other output). 
When the other commands talk about naming a wallet, this is what it actually means. 
You are welcome to use the first 16 characters of the hash of the public key for this assignment; you don't need to use the entire hash. 
The file name of the wallet file will be provided as an additional command line parameter.
"""
def address(walletName):
    walletTag = getWalletTag(walletName)
    print(walletTag)
    return


"""
Fund wallets (fund): this allows us to add as much money as we want to a wallet. While this is obviously not practical in the real world, 
it will allow us to test your program. (Although there still needs to be a way to fund wallets in the real world also.) 
Create a special case ID ('bigfoot', 'daddy_warbucks', 'lotto', or whatever) that your program knows to use as the source for a fund request, 
and also knows not to verify when handling verification, below. This means that 'bigfoot' (or whatever) will appear alongside the hash of the public keys as the source of funds. 
This function will be provided with three additional command line parameters: the destination wallet address, the amount to transfer, and the file name to save the transaction statement to.
"""
def fund(destWallet, amt, filename):
    time = str(datetime.now())
    tranFile = open(filename, 'w')
    sign = '0'
    print('From: ZSociety \nTo: %.16s \nAmount: %.2f \nDate: %s \n\n%s \n' % (destWallet, float(amt), time, sign), file = tranFile)
    print('ZSociety funded %.2f to %.16s' % (float(amt), destWallet))
    tranFile.close()
    return

    
"""
Transfer funds (transfer): this is how we pay with our cryptocurrency. 
It will be provided with four additional command line parameters: 
the source wallet file name (not the address!), the destination wallet address (not the file name!), 
the amount to transfer, and the file name to save the transaction statement to. 
Any reasonable format for the transaction statement is fine for this, as long as the transaction statement is text and thus readable by a human. 
Recall that it must have five pieces of information, described above in the "Transaction statement versus transaction record" section. 
Note that this command does NOT add anything to the ledger.
"""
def transfer(srcWalletName, destWalletAddr, amt, filename):
    time = str(datetime.now())
    tranFile = open(filename, 'w')
    sign = bytesToString(rsa.sign(('From: %.16s \nTo: %.16s \nAmount: %.2f \nDate: %s \n' % ((getWalletTag(srcWalletName)), destWalletAddr, float(amt), time)).encode('ascii'), loadWallet(srcWalletName)[1], 'SHA-256'))
    print('From: %.16s \nTo: %.16s \nAmount: %s \nDate: %s \n\n%s \n' % (getWalletTag(srcWalletName), destWalletAddr, amt, time, sign), file = tranFile)
    tranFile.close()
    return


"""
Check a balance (balance): based on the transactions in the block chain AND ALSO in the ledger, compute the balance for the provided wallet. 
This does not look at transaction statements, only the transaction records in the blocks and the ledger. 
The wallet address to compute the balance for is provided as an additional command line parameter.
"""
def balance(walletAddr):
    balance = 0
    blocknum = countBlocks()
    
    for i in range(blocknum):
        blockFile = open('block_' + str(i) + '.txt','r')
        for line in blockFile:
            if len(line.split(' ')) > 3:
                src, amt, dest = parseRecord(line)
                if src == walletAddr:
                    balance -= float(amt)
                if dest == walletAddr:
                    balance+= float(amt)
        blockFile.close()
    ledgerFile = open('ledger.txt', 'r')
    for line in ledgerFile:
            if len(line.split(' ')) > 3:
                src, amt, dest = parseRecord(line)
                if src == walletAddr:
                    balance -= float(amt)
                if dest == walletAddr:
                    balance+= float(amt)
    ledgerFile.close()
    print('Balance for wallet %.16s is %.2f' % (walletAddr, balance))
    return balance

"""
Verify a transaction (verify): verify that a given transaction statement is valid, which will require checking the signature and the availability of funds. 
Once verified, it should be added to the ledger as a transaction record. This is the only way that items are added to the ledger. 
The wallet file name (whichever wallet created the transaction) and the transaction statement being verified are the additional command line parameters.
"""
def verify(walletName, statement):

    pubkey = loadWallet(walletName)[0]

    f = open(statement, 'r')
    ledgerFile = open('ledger.txt', 'a')
    src = f.readline().split(' ')[1]
    dest = f.readline().split(' ')[1]
    amt = f.readline().split(' ')[1]
    dateParts = f.readline().split(' ')
    date = dateParts[1]+ ' ' + dateParts[2]
    f.readline() ## skip blank space
    signature = f.readline().split(' ')[0]
    try:
        if src == 'ZSociety':
            print('%.16s transferred %s to %.16s on %s \n' % (src, amt, dest, date), file = ledgerFile)
            print('Funding Transactions are always valid.')
        elif rsa.verify(('From: %.16s \nTo: %.16s \nAmount: %.2f \nDate: %s \n' % (src[:16], dest[:16], float(amt), date)).encode('ascii'), stringToBytes(signature[2:260]), pubkey):
            print('%.16s transferred %s to %.16s on %s \n' % (src, amt, dest, date), file = ledgerFile)
            print('Transaction Verified.')
        else:
            print('Invalid Transaction')
    except:
        print("Invalid Transaction")
    ledgerFile.close()
    f.close()


"""
Create, mine, and sign block (mine): this will form another block in the blockchain. The ledger will be emptied of transaction records, as they will all go into the current block being computed. 
A nonce will have to be computed to ensure the hash is below a given value. Recall that the first line in any block is the SHA-256 of the last block file. 
The difficulty for the mining will be the additional parameter to this command. For simplicity, the difficulty will be the number of leading zeros to have in the hash value -- 
so a value of 3 would imply that the hash must start with three leading zeros. We will be using very small difficulties here, so a brute-force method for finding the nonce is sufficient. 
The nonce must be a single unsigned 32 bit (or 64 bit) integer.
"""
def mine(difficulty):
    blocknum = countBlocks()
    target = int(difficulty)*'0'
    nonce=0
    fileHash = '111111111111'
    blockFile = open('block_' + str(blocknum) + '.txt', 'w') #create file if doesnt exist
    blockFile.close()
    while (hashFile('block_' + str(blocknum) + '.txt'))[:int(difficulty)] != target:
        nonce+=1
        blockFile = open('block_' + str(blocknum) + '.txt', 'w')
        print(hashFile('block_' + str(blocknum-1) + '.txt') + ' \n\n', file = blockFile)
        ledgerFile = open('ledger.txt', 'r')
        print('%s\n' % (ledgerFile.read()), file = blockFile)
        print('nonce: ' + str(nonce), file = blockFile)
        blockFile.close()
    ledgerFile = open("ledger.txt","w")
    ledgerFile.close()
    print('Ledger transactions moved to block_' + str(blocknum) + '.txt and mined with difficulty ' + str(difficulty) + ' and nonce ' + str(nonce))
    blocknum+=1


"""
Validate the blockchain (validate): this should go through the entire block chain, validating each one. 
This means that starting with block 1 (the block after the genesis block), 
ensure that the hash listed in that file, which is the hash for the previous block file, is correct. 
There are no additional command-line parameters for this function.
"""
def validate():
    blocknum = countBlocks()

    for b in range(1,blocknum):
        blockFile = open('block_' + str(b) + '.txt', 'r')
        if blockFile.readline().split(' ')[0] != hashFile('block_' + str(b-1) + '.txt'):
            print('Invalid block at block ' + str(b))
            return  
        blockFile.close()
    print ('Entire chain is valid')

if sys.argv[1] == 'name':
    name()
if sys.argv[1] == 'genesis':
    genesis()
if sys.argv[1] == 'generate':
    generate(sys.argv[2])
if sys.argv[1] == 'address':
    address(sys.argv[2])
if sys.argv[1] == 'fund':
    fund(sys.argv[2], sys.argv[3], sys.argv[4])
if sys.argv[1] == 'transfer':
    transfer(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
if sys.argv[1] == 'balance':
    balance(sys.argv[2])
if sys.argv[1] == 'verify':
    verify(sys.argv[2], sys.argv[3])
if sys.argv[1] == 'mine':
    mine(sys.argv[2])
if sys.argv[1] == 'validate':
    validate()