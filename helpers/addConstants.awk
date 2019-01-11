

#
# A little helper to put Numerical Constants into your data file 
# run like this
#
# gawk -F"," -f addConstants.awk files/UCIPowerPlant.csv >files/UCIPowerPlant_RNC.csv

BEGIN{OFS=FS}
NR == 1 {
	noTarget=$1
	for(i = 2; i < NF; i++){ 
		noTarget = noTarget OFS $i
		}	
	noTarget = noTarget OFS "0.1" OFS "0.2" OFS "0.3" OFS "0.4" OFS "0.5" OFS "0.6" OFS $NF
	print noTarget
}
NR > 1 {	
        noTarget=$1
        for(i = 2; i < NF; i++){  
                noTarget = noTarget OFS $i
                }
        noTarget = noTarget OFS "0" OFS "0" OFS "0" OFS "0" OFS "0" OFS "0" OFS $NF
        print noTarget
}
