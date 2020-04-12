NUM_DAYS=120
INIT_FRAC_INFECTED=0.001
INCUBATION_PERIOD=2.25
MEAN_ASYMPTOMATIC_PERIOD=0.5
MEAN_SYMPTOMATIC_PERIOD=5
SYMPTOMATIC_FRACTION=0.67
MEAN_HOSPITAL_REGULAR_PERIOD=8
MEAN_HOSPITAL_CRITICAL_PERIOD=8
COMPLIANCE_PROBABILITY=0.9
BETA_H=1.2410293733942703
BETA_W=0.9289438506612563
BETA_C=0.23195981755789088
BETA_S=1.8387669724845188
BETA_TRAVEL=0
HD_AREA_FACTOR=2.0
HD_AREA_EXPONENT=0
INTERVENTION=0
output_directory_base="outputs/test_output_timing"
input_directory="../simulator/input_files"
CALIBRATION_DELAY=10
DAYS_BEFORE_LOCKDOWN=0
# Set this to "--SEED_HD_AREA_POPULATION" to seed hd area population
# as well.
# SEED_HD_AREA_POPULATION="--SEED_HD_AREA_POPULATION"
SEED_HD_AREA_POPULATION=


usage(){
	echo "Usage: [ -i base_of_input_directory ] [ -o base_of_output_directory ]"
}

while getopts "hi:o:" option; do
	case ${option} in
		h)
			usage;
			exit 0;
			;;
		i)
			input_directory=${OPTARG};
			;;
		o)
			output_directory_base=${OPTARG};
			;;
		\?)
			usage;
			exit 1;
			;;
	esac;
done;

echo "Input directory is: ${input_directory}"
echo "Output directory is: ${output_directory_base}"

for INTERVENTION in  0 3 7 8 9 10; #`seq 3 3`;
do
	echo "Running with INTERVENTION=${INTERVENTION}..."
	output_directory="${output_directory_base}/intervention_${INTERVENTION}"
	if [ ! -d "${output_directory}" ];
	then
		mkdir -p "${output_directory}";
	fi;
	echo "Output will be genrerated for this intervention in ${output_directory}."
	command="time ./drive_simulator \
     $SEED_HD_AREA_POPULATION \
	 --NUM_DAYS $NUM_DAYS \
	 --INIT_FRAC_INFECTED $INIT_FRAC_INFECTED \
	 --INCUBATION_PERIOD $INCUBATION_PERIOD \
	 --MEAN_ASYMPTOMATIC_PERIOD $MEAN_ASYMPTOMATIC_PERIOD \
	 --MEAN_SYMPTOMATIC_PERIOD $MEAN_SYMPTOMATIC_PERIOD \
	 --SYMPTOMATIC_FRACTION $SYMPTOMATIC_FRACTION \
	 --MEAN_HOSPITAL_REGULAR_PERIOD $MEAN_HOSPITAL_REGULAR_PERIOD \
	 --MEAN_HOSPITAL_CRITICAL_PERIOD $MEAN_HOSPITAL_CRITICAL_PERIOD \
	 --COMPLIANCE_PROBABILITY $COMPLIANCE_PROBABILITY \
	 --BETA_H $BETA_H \
	 --BETA_W $BETA_W \
	 --BETA_C $BETA_C \
	 --BETA_S $BETA_S \
	 --BETA_TRAVEL $BETA_TRAVEL \
	 --HD_AREA_FACTOR $HD_AREA_FACTOR \
	 --HD_AREA_EXPONENT $HD_AREA_EXPONENT \
	 --INTERVENTION $INTERVENTION \
	 --output_directory $output_directory \
	 --input_directory $input_directory\
	 --CALIBRATION_DELAY $CALIBRATION_DELAY\
	 --DAYS_BEFORE_LOCKDOWN $DAYS_BEFORE_LOCKDOWN"

	echo $command;
	if eval $command; then
		echo "Simulation over for INTERVENTION=${INTERVENTION}."
		cur=`pwd`;
		cd $output_directory

		command="${GPLOT_PATH}gnuplot gnuplot_script.gnuplot"
		echo $command;
		if eval $command; then
			echo "Plots generated successfully for INTERVENTION=${INTERVENTION}."
		fi;
		cd "$cur";
	else
		echo "error with INTERVENTION=${INTERVENTION}: see above for output"
	fi;
	echo "Done with INTERVENTION=${INTERVENTION}"
	echo "*****************"
	echo "*****************"
done;

echo "Now plotting consolidated plots for all interventions"
python plot_all_interventions.py "${output_directory_base}"

