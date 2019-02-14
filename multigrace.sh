echo "with g0" > template.par
i=0
for var in "$@"
do
	echo " s$i legend \"$var\"" >> template.par
	i=$((i+1))	
done

xmgrace -param template.par $@
