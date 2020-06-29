#!/bin/bash

# the first command-line parameter is in $1, the second in $2, etc.

case "$1" in

    name) python mattcoin.py name
	  # additional parameters provided: (none)
	  ;;

    genesis) python mattcoin.py genesis block_0.txt
	     # additional parameters provided: (none)
             ;;

    generate) python mattcoin.py generate $2
	      # additional parameters provided: the wallet file name
              ;;

    address) python mattcoin.py address $2
	     # additional parameters provided: the file name of the wallet
	     ;;

    fund) python mattcoin.py fund $2 $3 $4
	  # additional parameters provided: destination wallet
	  # address, the amount, and the transaction file name
          ;;

    transfer) python mattcoin.py transfer $2 $3 $4 $5
	      # additional parameters provided: source wallet file
	      # name, destination address, amount, and the transaction
	      # file name
	      ;;

    balance) python mattcoin.py balance $2
	     # additional parameters provided: wallet address
	     ;;

    verify) python mattcoin.py verify $2 $3
	    # additional parameters provided: wallet file name,
	    # transaction file name
	    ;;

    mine) python mattcoin.py mine $2
		 # additional parameters provided: difficulty
		 ;;
    
    validate) python mattcoin.py validate
	      # additional parameters provided: (none)
	      ;;

    *) echo Unknown function: $1
       ;;

esac
