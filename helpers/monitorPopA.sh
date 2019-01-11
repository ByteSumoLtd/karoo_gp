

cd /home/andrew/karoo/myforks/karoo_gp_andrew/

# in the directory where Karoo_GP is writing the population_a files, you can monitor progress in terms of MSE using this oneliner: 
cat `ls -lat runs/files | head -2 | tail -1 |sed 's@^.* @runs\/files\/@; s@$@/population_a.csv@'` \
| grep fitness | sed 's/fitness,//; s/,.*$//'| grep -v "+" | sort -n | head -5

cd -

# old way of extracting lowest MSE was not working as well as the above...
#grep fitness | sed 's/fitness,//; s/,.*$//'| grep -v "+" | sort -nr | tail
