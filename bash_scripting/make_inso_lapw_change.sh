#!/bin/tcsh -f
# interface for making case.inso
unalias rm
set wffil = WFFIL
set llmax = 4
set ipr = 0
set kpot = 0
#set de 
#set errormas
#set lineint = 3
#set indexin1 = 1
#set iii
#set eneL
#set line
#set CHword = ""
#set indexoff = ""
#set atomcountWOSO
set file    = `pwd`
set file    = $file:t
if (-e $file.in1c && ! -z $file.in1c) then
 set filein1 = $file.in1c
else
 set filein1 = $file.in1
endif

#****************************find number of atoms with RLO **********************************

set noneqatom = `head -2 < $file.struct|tail -1|cut -c28-30`
set number_of_atoms_without_so = `head -1 < .infSO`

@ line = $number_of_atoms_without_so + 1
@ line = $line + $noneqatom
set atomname=`head -$line < .infSO | tail -$noneqatom`



#*****************************print information in case.inso**********************************

echo "$wffil" >> $file.inso
echo "$llmax  $ipr  $kpot                 llmax,ipr,kpot" >> $file.inso

if( $number_of_atoms_without_so == 0 ) then
  set atoms_without_so=
else
  @ line = $number_of_atoms_without_so + 1
  set atoms_without_so=`head -$line < .infSO | tail -$number_of_atoms_without_so`
endif

@ line = $noneqatom + $number_of_atoms_without_so
@ line = $line + 2
set emin = `head -$line < .infSO | tail -1`
@ line = $line + 1
set emax = `head -$line < .infSO | tail -1`
@ line = $line + 1
set hkl = `head -$line < .infSO | tail -1`
@ line = $line + 1
set numk = `head -$line < .infSO | tail -1`
@ line = $line + 1
set EMAX = `head -$line < .infSO | tail -1`
@ line = $line + 1
set localp = `head -$line < .infSO | tail -1`
#@ line = $line + 1
#set spinpo = `head -$line < .infSO | tail -1`
echo "$emin  $emax                Emin, Emax" >> $file.inso 
echo "    $hkl                           h,k,l (direction of magnetization)" >> $file.inso

if ( $localp == 'y' || $localp == 'c' ) then
 @ countatomRLO = $noneqatom - $number_of_atoms_without_so
else
 set countatomRLO = 0
 goto NO_RLO
endif

#*******************************find index of atoms for RLO********************************


set lineint = 3
set index = 1
Pinfnoneqatom:
if ( $index <= $noneqatom ) then

#*************find linerization energy ,de, and switch from case.in1(c)************

#echo index, lineint, $index,$lineint

#        set numberL = `head -$lineint < $filein1 | tail -1 |cut -c 11-13`
        set numberL1 = `head -$lineint < $filein1 | tail -1`
        set numberL = $numberL1[2]
        @ lineint = $numberL + $lineint

        set rlotest=1
        while($number_of_atoms_without_so >= $rlotest)
          if( $index == $atoms_without_so[$rlotest] ) goto down
          @ rlotest ++
        end

        head -$lineint < $filein1 | tail -$numberL > .infoL
        grep -w "1   " .infoL > .infoL1
        set lineL1 = `grep -w "1   " .infoL |wc -l `

         if ( $localp == 'y' && $lineL1 == 0 )  then
           @ countatomRLO = $countatomRLO - 1
           echo ">>>"
           echo ">>> ERROR: Your atom $index has no p-orbital!"
           echo ">>>"
           mv $file.inso .stopSO
           exit
         endif
 
        set ii = 1
        while ($ii <= $lineL1)
          set infLene1 = `tail -$ii < .infoL1 | head -1 |cut -c 6-12`
          set infLEINT1 = `echo "$infLene1*10"| bc -l | awk '{print int($1)}'`
          @ ii = $ii + 1

          set infLene2 = `tail -$ii < .infoL1 | head -1 |cut -c 6-12`
          set infLEINT2 = `echo "$infLene2*10"| bc -l | awk '{print int($1)}'`
            if ($infLEINT2 >= $infLEINT1)  then 
              @ iii = $ii - 1 
             else
              set iii = $ii
            endif 
              set eneL = `tail -$iii < .infoL1 | head -1 |cut -c 6-12` 
              set de = `tail -$iii < .infoL1 | head -1 |cut -c 16-21`
              set switch = `tail -$iii < .infoL1 | head -1 |cut -c 23-26`
          @ ii = $ii + 1
         end
        if ( $localp == 'c' && $lineL1 > 0 ) then
          echo "p-Energy parameters for $atomname[$index] atom is :" 
          grep -w "1   " .infoL1
          echo " "
          echo -n "Would you like to add RLO? (Y/n)"
          set cRLO = ( $< )
           if ( $cRLO == 'n' || $cRLO == 'N' ) then
            @ countatomRLO = $countatomRLO - 1
           goto down 
           endif  
        endif
        if ( $localp == 'c' && $lineL1 == 0 ) then
          echo " "
          echo "$atomname[$index] has no p-orbital and we can not add RLO."
          @ countatomRLO = $countatomRLO - 1
          goto down 
        endif
 echo "$index $eneL $de $switch             atom-number, E-param for RLO" >> .ieds
down:
        @ lineint = $lineint + 1
       @ index = $index + 1
       goto Pinfnoneqatom
endif 

#******************find number of atoms without SO and indexes of them**************************

NO_RLO:
echo " $countatomRLO                       number of atoms with RLO" >> $file.inso
if(-e .ieds) cat .ieds >> $file.inso


if( $number_of_atoms_without_so == 0 ) then
  echo $number_of_atoms_without_so $number_of_atoms_without_so "     number of atoms without SO, atomnumbers">> $file.inso
else
  @ line = $number_of_atoms_without_so + 1
  set atoms_without_so=`head -$line < .infSO | tail -$number_of_atoms_without_so`
  echo $number_of_atoms_without_so $atoms_without_so "     number of atoms without SO, atomnumbers">> $file.inso
endif


set emaxold = `grep VECTOR $filein1 |cut -c 30-39`
sed "/VECTOR/s/$emaxold/$EMAX/" $filein1 > .in1
mv .in1 $filein1

#******************************************************************************
if (-e "setEMAX_lapw") rm setEMAX_lapw
if (-e ".indexSO") rm .indexSO
if (-e ".infoL") rm .infoL
if (-e ".infoL1") rm .infoL1
if (-e ".ieds") rm .ieds
#*****************************************************************************
if ($status) goto error1

if($?EDITOR) then
  if ("$EDITOR" == vi ) then
    alias editor 'xterm -e vi'
  else
    alias editor '$EDITOR'
  endif
else
  alias editor emacs
endif





#########################################
# commenting out the editing steps to save time
#
#echo " Check the generated $file.inso file (RLOs,...)"
#sleep 1
#editor $file.inso

#echo " Check the generated $filein1 file (Emax and nband (if ELPA is used)"
#echo " at the bottom of the file)"
#sleep 1
#editor $filein1
#########################################


exit (0)
error:
echo ">>>"
echo ">>> ERROR: $errormas not found\!"
echo ">>> ERROR:"
echo ">>>"
exit (1)
error1:
echo ">>>"
echo "Stop error"
echo ">>>"
exit (2)
