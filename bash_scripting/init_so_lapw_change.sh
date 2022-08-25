#!/bin/tcsh -f
unalias rm
clear
set name      = $0
set bin       = $name:h		    #directory of WIEN-executables
#if !(-d $bin) set bin = .
set name      = $name:t 	    #name of this script-file
set logfile   = :log
set file      = `pwd`
set file      = $file:t		    #tail of file-names
set sleep     = 1                   # use 0 for fast machines
##################################################################################
#---> default flags
unset help		#set -> help output

#---> handling of input options
echo ">   ($name) options: $argv"	>> $logfile
alias sb 'shift; breaksw'	#definition used in switch
while ($#argv)
  switch ($1)
  case -[H|h]:
    set help; sb
  case -e: 
    shift; set stopafter=$1; sb
  case -s:
    shift; set next=$1; breaksw
# adding a case here if you want to bypass the user input 
  case -b:		#needs to be followed by mag dir
	shift; set MAGDIR=$1; sb
  default: 
    echo "ERROR: option $1 does not exist"; sb
  endsw
end
if ($?help) goto help









#=======================For Me====================================
set i = 1
set nkpoint = 1000
set emin = -10
set emax = 1.9
set hkl = ` echo "0 0 1"`
#=================================================================
#=======================For Me====================================
set errormas
set cmplx
if (-e ".stopSO") rm .stopSO
if (-e "$file.inso") rm $file.inso
if (-e ".indexSO") rm .indexSO
if (-e ".infL") rm .infoL
if (-e ".infoL1") rm .infoL1
if (-e $file.in1c && ! -z $file.in1c) then
 set filein1 = $file.in1c
 set cmplx='-c'
else
 set filein1 = $file.in1
  if ( -e $file.in2 ) then 
   cp $file.in2 $file.in2c
   echo "The file $file.in2c has been generated automatically"
  endif
endif
if !(-e $filein1) then 
 set errormas = $filein1
 goto error
endif


#==================================================================

if($?EDITOR) then
  if ("$EDITOR" == vi ) then
    alias editor 'xterm -e vi'
  else
    alias editor '$EDITOR'
  endif
else
  alias editor emacs
endif

#=================================For me==========================================
if !(-e $file.struct) then
   set errormas = $file.struct
   goto error
endif

if (-e ".infSO") rm .infSO
if (-e ".chkname") rm .chkname
#################################################################################

########### commenting out user input
#
#echo " "
#echo "---->Please select the direction of the moment ( h k l ) "
#echo -n "               (For R-lattice in R coordinates)(default $hkl): "
#set hkl = ($<)
###########


set hkl = `head -1 < mag_dir_inso.txt | tail -1`

echo ""
echo "The magnetization direction is ${hkl}"
echo ""


# Writes hkl to an interim file to be read by script later

echo "$hkl" > mag_dir.txt




set CHhkl = `echo "$hkl nu"`
#echo "$CHhkl"
if ( $CHhkl[1] == "nu" )  set hkl = ` echo "0 0 1"`

#################################################################################
set noneqatom = `head -2 < $file.struct|tail -1|cut -c28-30`
set conatom = 1
Pinfnoneqatom1:
if ( $conatom <= $noneqatom ) then
  set atomname = `grep Z: $file.struct|head -$conatom|tail -1|cut -c1-5 `
  echo "atom $conatom is $atomname"
  echo "$atomname" >> .chkname
  @ conatom = $conatom + 1
  goto Pinfnoneqatom1
endif
PSN:
echo " "
##################################################################################

########## commenting out user input
#
#echo  'Select  atom-numbers (1,2,3) or "ranges of atoms" (1-3,9-12) (without blanks) '
#echo  'for which you would NOT like to add SO interaction'
#echo -n ' (default none, just press "enter" ): '
#
##########


set natom=""
echo "Automatically select 0 for number of atoms without SO interaction"
echo ""

##################################################################################
if ( $#natom >= 2)  goto PSN
if ( $natom == "" )  then
 set natom = 0
 echo "$natom" >> .infSO
else
 rm -f .atomlist
 parseline_lapw $natom
 if ($status != 0 ) goto PSN 
 set test=`wc .atomlist`
 set natom=$test[1]
 if ( $natom > $noneqatom ) goto PSN
 echo "$natom" >> .infSO
 cat .atomlist >> .infSO
 rm .atomlist
endif


  set conatom = 1
  Pinfnoneqatom:
   if ( $conatom <= $noneqatom ) then
    set atomname = `grep Z: $file.struct|head -$conatom|tail -1|cut -c1-5 `
    echo "$atomname" >> .infSO
    @ conatom = $conatom + 1
    goto Pinfnoneqatom
  endif
###########################


echo ""

########## commenting out user inputs
#
#echo " "
#echo "For large spin orbit effects it might be necessary to include many more "
#echo "eigenstates from lapw1 by increasing EMAX in case.in1(c) - in case of "
#echo "MPI-parallel calculations with ELPA nband has to be increased instead."
#echo " "
#echo -n "---->Please enter EMAX(default 10.0 Ryd): "
#
##########

echo "The default EMAX value has been selected to be 10.0 Ryd"
echo ""

set EMAX = ""
if ( $EMAX == "" )  set EMAX = 10.0
echo "$emin" >> .infSO
echo "$emax" >> .infSO
echo "$hkl" >> .infSO
echo "" >> .infSO
echo "$EMAX" >> .infSO
echo " "

########## commenting out user inputs
#
#echo "The radial basis set for heavy atoms with p-semicore states is very"
#echo "limited. One can improve this by adding RLOs. Note: you MUST NOT add"
#echo "RLOs for atoms like oxygen,.... therefore the default is set to NONE"
#echo -n "---->Add RLO for NONE, ALL, CHOOSE elements? (N/a/c) [default a(all)]: "
#
##########


echo "RLO has been applied to all atoms by default. If atoms like oxygen are included"
echo "This must be edited accordingly."
echo ""



set localp = ""
if ( $localp == "" ) set localp = a
  switch ($localp)
  case [a|A]:
    echo 'y' >> .infSO
    breaksw 
  case [n|N]: 
   echo 'n' >> .infSO
   breaksw
  case [c|C]:
   echo 'c' >> .infSO
   breaksw
  endsw

#=============================for me=========================================
make_inso_lapw
if ( -e .stopSO ) then
rm .stopSO
exit
endif
#============================================================================

cat<<EOF

In spinpolarized case SO may reduce symmetry. 

The program symmetso detects the proper symmetry and creates new struct and
input files. (Note, equivalent atoms could become inequivalent in some cases). 

EOF


########## Commenting out user inputs
#
#echo -n "Do you have a spinpolarized case (and want to run symmetso) ? (y/N) (default y)"
#set yn = ($<)
#
##########
# sets a default value to yes:


set yn = ""
echo "Since it is likely a spin-polarized case, symmetso will be run"
echo ""


if ($yn == "") then
  set yn = y

if ($yn == y || $yn == Y) then
  x_lapw symmetso $cmplx
  
  ############# commenting out the editor line to save time
  
  #editor $file.outsymso
  
  #############
  set natold=`head -2 $file.struct | tail -1 | cut -c28-30`
  set natnew=`head -2 $file.struct_so | tail -1 | cut -c28-30`
  if($natold == $natnew) then
    echo "The number of non-equivalent atoms did not change"
    unset changed_atoms
  else
    set changed_atoms
    echo "The number of non-equivalent atoms changed from $natold to $natnew "
  endif
  echo " A new structure for SO calculations has been created (_so)."
  echo " If you commit it will create new  $file.struct, in1(c), in2c, inc," 
  echo " clmsum/up/dn, vspup/dn, vnsup/dn, tausum/up/dn and r2v/dn files."
  echo " (Please SAVE any previous calculations)"
  echo ""
  ########### commenting out user inputs
  #
  #echo "NOTE: Files for -orb ($file.indm(c),inorb,dmatup/dn) must be adapted manually" 
  #echo -n "Do you want to use the new structure for SO calculations ? (y/N) (default y)"
  #set yn = ($<)
  #
  ###########
  # sets a default value to yes
  
  echo "The new structure created by symmetso will be used for SO calculations"
  echo ""
  
  set yn = ""
  
  if ($yn == "") then 
	set yn = y
  if ($yn == y || $yn == Y) then
     cp $file.struct_so $file.struct
     if(! -z $file.ksym ) then
        echo ""
        echo " initso detected $file.ksym, which contains proper symmetry operations"
        echo " for KGEN. NOTE: WHEN YOU CHANGE THE KMESH LATER ON, YOU MUST RUN:"
        echo " x kgen -so ;  to use the symmetry operations in $file.ksym"
        echo " Please note: by default initso will try to generate shifted k-meshes."
        echo " In certain cases this could lead to problems, so you may want to check"
        echo " later with unshifted meshes. "
rerunkgen:
#==============================For Me========================================
        if (-e $file.klist && ! -z $file.klist && `head -1 < $file.klist | cut -c69-75` == 0) then
           set nkpoint = `awk '{sum+=$6} END{print sum}' $file.klist`
           echo " "
           echo "Number of Kpoint in $file.klist is : $nkpoint"
        else if (-e $file.klist && ! -z $file.klist) then
           set nkpoint = `head -1 < $file.klist | cut -c69-75`
           echo " "
           echo "Number of Kpoint in $file.klist is : $nkpoint"
        endif
		
		
        echo ""
		
		######### commenting out user inputs
		#
        #echo -n "---->Please enter Number of k-points in full BZ (default: $nkpoint): "
		#
		#########
        set numk = ""
		
		
        if ( $numk == "" )  set numk = $nkpoint
        x kgen -d -so -fbz    #I have edited this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        kgen kgen.def << EOF
$numk
0
EOF
        if ($status) goto error1
		
		########## commenting out editor line to save time
        #editor $file.klist
		##########
		
		########## commenting out user inputs
		#
        #echo -n "Do you want to rerun kgen ? (y/N) (default n)"
		#
        set yn = "n"
        if ($yn == y || $yn == Y) then
          goto rerunkgen
        endif
     else
 #   ksym not present **********************
        echo ""
        echo " We run KGEN to generate a new kmesh for the SO calculation:"
        echo " Please note: by default initso will try to generate shifted k-meshes."
        echo " In certain cases this could lead to problems, so you may want to check"
        echo " later with unshifted meshes. "

rerunkgen1:
#============================for me========================================
        if (-e $file.klist && ! -z $file.klist) then
           set nkpoint = `head -1 < $file.klist |cut -c69-75`
           echo " "
           echo "Number of Kpoint in $file.klist is : $nkpoint"
         endif
         echo ""
		 
		 ########## commenting out user inputs
		 #
         #echo -n "---->Please enter Number of k-points in full BZ (default: $nkpoint): "
		 #
		 ##########
         set numk = ""
         if ( $numk == "" )  set numk = $nkpoint
#clear
#echo "MORTEZA"
#**********************
         x kgen -d
         kgen kgen.def << EOF
$numk
0                     
EOF

# THE ABOVE MAY BE THE THING TO CHANGE ( I AM CHANGING FROM 1 ----> 0)


#**********************
         if ($status) goto error1
	
		########### commenting out editor line to save time
        #editor $file.klist
		###########
		
		########### commenting out user inputs
		#
        # echo -n "Do you want to rerun kgen ? (y/N) (default n)"
		#
		###########
         set yn = ""
         if ($yn == y || $yn == Y) then
            goto rerunkgen1
         endif

     endif
     if( -e $file.inc_so && ! -z $file.inc_so ) mv $file.inc_so $file.inc
     if( -e $file.in2c_so && ! -z $file.in2c_so ) mv $file.in2c_so $file.in2c
     if(! -e $file.in2c_so &&  -e $file.in2_so && ! -z $file.in2c_so  && ! -z $file.in2_so ) cp $file.in2_so $file.in2c
     if(! -e $file.in2c_so &&  -e $file.in2_so && ! -z $file.in2c_so  && ! -z $file.in2_so ) mv $file.in2_so $file.in2
     if( -e $file.in1c_so && ! -z $file.in1c_so ) mv $file.in1c_so $file.in1c
     if( -e $file.in1_so  && ! -z $file.in1_so ) mv $file.in1_so $file.in1
     if( -e $file.clmsum_so  && ! -z $file.clmsum_so) mv $file.clmsum_so $file.clmsum
     if( -e $file.clmup_so  && ! -z $file.clmup_so) mv $file.clmup_so $file.clmup
     if( -e $file.clmdn_so  && ! -z $file.clmdn_so) mv $file.clmdn_so $file.clmdn
     if( -e $file.vspup_so  && ! -z $file.vspup_so) mv $file.vspup_so $file.vspup
     if( -e $file.vspdn_so  && ! -z $file.vspdn_so) mv $file.vspdn_so $file.vspdn
     if( -e $file.vnsup_so  && ! -z $file.vnsup_so) mv $file.vnsup_so $file.vnsup
     if( -e $file.vnsdn_so  && ! -z $file.vnsdn_so) mv $file.vnsdn_so $file.vnsdn
     if( -e $file.tausum_so  && ! -z $file.tausum_so) mv $file.tausum_so $file.tausum
     if( -e $file.tauup_so  && ! -z $file.tauup_so) mv $file.tauup_so $file.tauup
     if( -e $file.taudn_so  && ! -z $file.taudn_so) mv $file.taudn_so $file.taudn
     if( -e $file.r2v_so  && ! -z $file.r2v_so) mv $file.r2v_so $file.r2v
     if( -e $file.r2vdn_so  && ! -z $file.r2vdn_so) mv $file.r2vdn_so $file.r2vdn
     if( -e $file.recprlist ) rm $file.recprlist
     if( -e $file.indm ) cp $file.indm $file.indmc 
     if($?changed_atoms) then
        echo "The number of non-equivalent atoms has changed \!\!\!"
        if( -e $file.indm || -e $file.indmc ) then
            echo "Please adapt $file.indmc manually to this changed atom-list"
            echo "Please adapt $file.inorb manually" 
        endif
        echo "please adapt $file.inso manually in case of atom-specific input (RLOs)" 
     endif
     echo "For a cubic case, it is more safe to start the first scf-cycle"
     echo "using    runsp -so -s lapw1 (to avoid EFG-MATRIX IST DIE NULLMATRIX error)"
  endif
endif
#============================================================================

cat<<EOF

Spinorbit is now ready to run.
EOF

exit 0

error:
    echo "An error has occured"
    if("$#errormas" > 0) echo "file  $errormas   missing"
exit 1

error1:
echo ">>>"
echo "Stop error"
echo ">>>"
exit (2)

help:					#help exit 
cat << theend 

PROGRAM:	$0

PURPOSE:	initialisation of spinorbit
		to be called within the case-directory

USAGE:		$name

FLAGS:
-h/-H ->	help
		
theend

exit 1


