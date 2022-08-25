#!/bin/bash

# Author : Ben Rasmussen
# Email : ben.f.rasmussen@gmail.com
# Copyright :
# Script follows here:

echo ""
echo "************************************"
echo "*                                  *"
echo "* This script runs a cycle of non- *"
echo "*   scf calculation with a desired *"
echo "*  set of magnetization directions *" 
echo "*                                  *"
echo "************************************"
echo ""

# for the saved file head, the current working directory tail is used 
# as follows:

FILEHEAD=${PWD##*/}
FILEHEAD=${FILEHEAD:-/}


# insert the desired magnetization direction here as an array:

MagList=("0 1 2" "0 1 4" "0 1 -1" "0 1 -2" "0 1 -3" "0 1 -4" "0 2 1" "0 2 4" "0 2 -1" "0 
2 -2" "0 2 -3" "0 2 -4" "0 4 1" "0 4 2" "0 4 -1" "0 4 -2" "0 4 -3" "0 4 -4" "0 -1 1" "0 
-1 2" "0 -1 4" "0 -1 -2" "0 -1 -3" "0 -1 -4" "0 -2 1" "0 -2 2" "0 -2 4" "0 -2 -1" "0 -2 
-3" "0 -2 -4" "0 -3 1" "0 -3 2" "0 -3 4" "0 -3 -1" "0 -3 -2" "0 -3 -4" "0 -4 1" "0 -4 2" 
"0 -4 4" "0 -4 -1" "0 -4 -2" "0 -4 -3" "1 0 2" "1 0 4" "1 0 -1" "1 0 -2" "1 0 -3" "1 0 -4"
 "1 2 0" "1 2 4" "1 2 -1" "1 2 -2" "1 2 -3" "1 2 -4" "1 4 0" "1 4 2" "1 4 -1" "1 4 -2" "1 
4 -3" "1 4 -4" "1 -1 0" "1 -1 2" "1 -1 4" "1 -1 -2" "1 -1 -3" "1 -1 -4" "1 -2 0" "1 -2 2" 
"1 -2 4" "1 -2 -1" "1 -2 -3" "1 -2 -4" "1 -3 0" "1 -3 2" "1 -3 4" "1 -3 -1" "1 -3 -2" "1 
-3 -4" "1 -4 0" "1 -4 2" "1 -4 4" "1 -4 -1" "1 -4 -2" "1 -4 -3" "2 0 1" "2 0 4" "2 0 -1" 
"2 0 -2" "2 0 -3" "2 0 -4" "2 1 0" "2 1 4" "2 1 -1" "2 1 -2" "2 1 -3" "2 1 -4" "2 4 0" "2 
4 1" "2 4 -1" "2 4 -2" "2 4 -3" "2 4 -4" "2 -1 0" "2 -1 1" "2 -1 4" "2 -1 -2" "2 -1 -3" 
"2 -1 -4" "2 -2 0" "2 -2 1" "2 -2 4" "2 -2 -1" "2 -2 -3" "2 -2 -4" "2 -3 0" "2 -3 1" "2 
-3 4" "2 -3 -1" "2 -3 -2" "2 -3 -4" "2 -4 0" "2 -4 1" "2 -4 4" "2 -4 -1" "2 -4 -2" "2 -4 
-3" "4 0 1" "4 0 2" "4 0 -1" "4 0 -2" "4 0 -3" "4 0 -4" "4 1 0" "4 1 2" "4 1 -1" "4 1 -2" 
"4 1 -3" "4 1 -4" "4 2 0" "4 2 1" "4 2 -1" "4 2 -2" "4 2 -3" "4 2 -4" "4 -1 0" "4 -1 1" 
"4 -1 2" "4 -1 -2" "4 -1 -3" "4 -1 -4" "4 -2 0" "4 -2 1" "4 -2 2" "4 -2 -1" "4 -2 -3" "4 
-2 -4" "4 -3 0" "4 -3 1" "4 -3 2" "4 -3 -1" "4 -3 -2" "4 -3 -4" "4 -4 0" "4 -4 1" "4 -4 2"
 "4 -4 -1" "4 -4 -2" "4 -4 -3" "-1 0 1" "-1 0 2" "-1 0 4" "-1 0 -2" "-1 0 -3" "-1 0 -4" 
"-1 1 0" "-1 1 2" "-1 1 4" "-1 1 -2" "-1 1 -3" "-1 1 -4" "-1 2 0" "-1 2 1" "-1 2 4" "-1 2 
-2" "-1 2 -3" "-1 2 -4" "-1 4 0" "-1 4 1" "-1 4 2" "-1 4 -2" "-1 4 -3" "-1 4 -4" "-1 -2 0"
 "-1 -2 1" "-1 -2 2" "-1 -2 4" "-1 -2 -3" "-1 -2 -4" "-1 -3 0" "-1 -3 1" "-1 -3 2" "-1 -3 
4" "-1 -3 -2" "-1 -3 -4" "-1 -4 0" "-1 -4 1" "-1 -4 2" "-1 -4 4" "-1 -4 -2" "-1 -4 -3" 
"-2 0 1" "-2 0 2" "-2 0 4" "-2 0 -1" "-2 0 -3" "-2 0 -4" "-2 1 0" "-2 1 2" "-2 1 4" "-2 1 
-1" "-2 1 -3" "-2 1 -4" "-2 2 0" "-2 2 1" "-2 2 4" "-2 2 -1" "-2 2 -3" "-2 2 -4" "-2 4 0" 
"-2 4 1" "-2 4 2" "-2 4 -1" "-2 4 -3" "-2 4 -4" "-2 -1 0" "-2 -1 1" "-2 -1 2" "-2 -1 4" 
"-2 -1 -3" "-2 -1 -4" "-2 -3 0" "-2 -3 1" "-2 -3 2" "-2 -3 4" "-2 -3 -1" "-2 -3 -4" "-2 
-4 0" "-2 -4 1" "-2 -4 2" "-2 -4 4" "-2 -4 -1" "-2 -4 -3" "-3 0 1" "-3 0 2" "-3 0 4" "-3 
0 -1" "-3 0 -2" "-3 0 -4" "-3 1 0" "-3 1 2" "-3 1 4" "-3 1 -1" "-3 1 -2" "-3 1 -4" "-3 2 
0" "-3 2 1" "-3 2 4" "-3 2 -1" "-3 2 -2" "-3 2 -4" "-3 4 0" "-3 4 1" "-3 4 2" "-3 4 -1" 
"-3 4 -2" "-3 4 -4" "-3 -1 0" "-3 -1 1" "-3 -1 2" "-3 -1 4" "-3 -1 -2" "-3 -1 -4" "-3 -2 
0" "-3 -2 1" "-3 -2 2" "-3 -2 4" "-3 -2 -1" "-3 -2 -4" "-3 -4 0" "-3 -4 1" "-3 -4 2" "-3 
-4 4" "-3 -4 -1" "-3 -4 -2" "-4 0 1" "-4 0 2" "-4 0 4" "-4 0 -1" "-4 0 -2" "-4 0 -3" "-4 
1 0" "-4 1 2" "-4 1 4" "-4 1 -1" "-4 1 -2" "-4 1 -3" "-4 2 0" "-4 2 1" "-4 2 4" "-4 2 -1" 
"-4 2 -2" "-4 2 -3" "-4 4 0" "-4 4 1" "-4 4 2" "-4 4 -1" "-4 4 -2" "-4 4 -3" "-4 -1 0" 
"-4 -1 1" "-4 -1 2" "-4 -1 4" "-4 -1 -2" "-4 -1 -3" "-4 -2 0" "-4 -2 1" "-4 -2 2" "-4 -2 
4" "-4 -2 -1" "-4 -2 -3" "-4 -3 0" "-4 -3 1" "-4 -3 2" "-4 -3 4" "-4 -3 -1" "-4 -3 -2")

# loop that runs through every desired magnetization direction
# and performs the calculation and save for the directions in WIEN:

for mag in ${!MagList[@]};
do 
#echo "mag $mag is ${MagList[$mag]}"
echo ${MagList[$mag]} > mag_dir_inso.txt

# Runs init_so_lapw with plenty of user input. Insert desired Mag. Dir.

init_so_lapw

MagList_length=${#MagList[@]}

# reads the magnitization direction based on the assigned value in initso_lapw

MAGDIR=$(head -n 1 mag_dir.txt)
TRIMMAGDIR=$(echo $MAGDIR | tr -d ' ')

# prints off magnetization direction chosen as an environment variable
# as a sanity check and prints out a progress report:

#echo "scale=3 ${mag} / ${MagList_length}" | bc

echo ""
echo ""
echo "*******************************************************************"
echo "*  The Magnetocrystalline anisotropy script has ran ${mag} time(s)     *"
echo "*       out of a total of ${MagList_length} magnetizations directions           *"
echo "*                                                                 *"
echo "*     The current magnetization direction being calculated is:    *"
echo "*                                                                 *"                          
echo "*                              $TRIMMAGDIR                                *" 
echo "*                                                                 *"
#echo "*       The percentage that has then been completed is:            *"
#echo "*                   scale=2 ${mag} / ${MagList_length}                             *" | bc    
echo "*                                                                 *"
echo "*******************************************************************"                                    





# MAE protocol for a spin-polarized calculation:

x lapw1 -up
x lapw1 -dn
x lapwso -up -orb
x lapw2 -so -up
x lapw2 -so -dn

# saves the file using the environment variable set above

filename="${FILEHEAD}_${TRIMMAGDIR}"
echo "$filename"

save_lapw "${FILEHEAD}_${TRIMMAGDIR}" # add -s here if a silent save is needed

# Built in search command for WIEN can be used to find the desired :SUM

grepline_lapw :SUM "$FILEHEAD*.scf2*" 2

# Writes all of the data into a single file that will need to be processed 
# using the MAE processing script or otherwise:

done

grepline_lapw :SUM "$FILEHEAD*.scf2*" 2 > "${FILEHEAD}_anisotropy_data.txt"

# the important partss of this script can be run as a single command below
# x lapw1 -up && x lapw1 -dn && x lapwso -up -orb && x lapw2 -up -so && x lapw2 -dn -so
#                   + save_lapw hcp_cobalt_xxx -s

