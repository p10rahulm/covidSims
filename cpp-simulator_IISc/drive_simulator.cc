#include "simulator.h"
#include "outputs.h"
#include "defaults.h"
#include <cassert>
#include <iostream>
#include <fstream>
#include <string>
#include <cxxopts.hpp>

// Input Arguments
// 1: NUM_DAYS
// 2: INIT_FRAC_INFECTED
// 3: INCUBATION_PERIOD
// 4: MEAN_ASYMPTOMATIC_PERIOD
// 5: MEAN_SYMPTOMATIC_PERIOD
// 6: SYMPTOMATIC_FRACTION
// 7: MEAN_HOSPITAL_REGULAR_PERIOD
// 8: MEAN_HOSPITAL_CRITICAL_PERIOD
// 9: COMPLIANCE_PROBABILITY
// 10: BETA_H
// 11: BETA_W
// 12: BETA_C
// 13: BETA_S
// 14: BETA_TRAVEL
// 15: HD_AREA_FACTOR
// 16: HD_AREA_EXPONENT
// 17: INTERVENTION
// 18: output directory
// 19: input directory

int main(int argc, char** argv){

  cxxopts::Options options(argv[0],
						  "Simulate the mean field agent model");

  options.add_options()
	("h,help", "display description of program options")
	("SEED_HD_AREA_POPULATION", "seed those living in high-density areas as well",
	 cxxopts::value<bool>()->default_value(DEFAULTS.SEED_HD_AREA_POPULATION))
	("NUM_DAYS", "number of days in the simulation",
	 cxxopts::value<count_type>()->default_value(DEFAULTS.NUM_DAYS))
	("INIT_FRAC_INFECTED", "initial probability of a person being infected",
	 cxxopts::value<double>()->default_value(DEFAULTS.INIT_FRAC_INFECTED))
	("INCUBATION_PERIOD", "incubation period",
	 cxxopts::value<double>()->default_value(DEFAULTS.INCUBATION_PERIOD))
	("MEAN_ASYMPTOMATIC_PERIOD", "mean asymptomati period",
	 cxxopts::value<double>()->default_value(DEFAULTS.MEAN_ASYMPTOMATIC_PERIOD))
	("MEAN_SYMPTOMATIC_PERIOD", "mean symptomatic period",
	 cxxopts::value<double>()->default_value(DEFAULTS.MEAN_SYMPTOMATIC_PERIOD))
	("SYMPTOMATIC_FRACTION", "fraction of people who develop symptoms",
	 cxxopts::value<double>()->default_value(DEFAULTS.SYMPTOMATIC_FRACTION))
	("MEAN_HOSPITAL_REGULAR_PERIOD", "mean period of regular hospitalization",
	 cxxopts::value<double>()->default_value(DEFAULTS.MEAN_HOSPITAL_REGULAR_PERIOD))
	("MEAN_HOSPITAL_CRITICAL_PERIOD", "mean period of critical care hospitalization",
	 cxxopts::value<double>()->default_value(DEFAULTS.MEAN_HOSPITAL_CRITICAL_PERIOD))
	("COMPLIANCE_PROBABILITY", "default compliance probability",
	 cxxopts::value<double>()->default_value(DEFAULTS.COMPLIANCE_PROBABILITY))
	("BETA_H", "the beta_home parameter",
	 cxxopts::value<double>()->default_value(DEFAULTS.BETA_H))
	("BETA_W", "the beta_workplace parameter",
	 cxxopts::value<double>()->default_value(DEFAULTS.BETA_W))
	("BETA_C", "the beta_community parameter",
	 cxxopts::value<double>()->default_value(DEFAULTS.BETA_C))
	("BETA_S", "the beta_school parameter",
	 cxxopts::value<double>()->default_value(DEFAULTS.BETA_S))
	("BETA_TRAVEL", "the beta_travel parameter",
	 cxxopts::value<double>()->default_value(DEFAULTS.BETA_TRAVEL))
	("HD_AREA_FACTOR", "multiplicative factor for high density areas",
	 cxxopts::value<double>()->default_value(DEFAULTS.HD_AREA_FACTOR))
	("HD_AREA_EXPONENT", "exponent for community size for high density areas",
	 cxxopts::value<double>()->default_value(DEFAULTS.HD_AREA_EXPONENT))
	("INTERVENTION", "index of the intervention",
	 cxxopts::value<count_type>()->default_value(DEFAULTS.INTERVENTION))
	("output_directory", "output directory",
	 cxxopts::value<std::string>()->default_value(DEFAULTS.output_dir))
	("input_directory", "input directory",
	 cxxopts::value<std::string>()->default_value(DEFAULTS.input_base))
	("CALIBRATION_DELAY", "delay observed in calibration.",
	cxxopts::value<double>()->default_value(DEFAULTS.CALIBRATION_DELAY))
	("DAYS_BEFORE_LOCKDOWN", "no intervention period prior to interventions",
	cxxopts::value<double>()->default_value(DEFAULTS.DAYS_BEFORE_LOCKDOWN));
  
  auto optvals = options.parse(argc, argv);
  
  if(optvals.count("help")){
	std::cout << options.help() << std::endl;
	return 0;
  }
  
  //Save options
  GLOBAL.NUM_DAYS = optvals["NUM_DAYS"].as<count_type>();
  GLOBAL.INIT_FRAC_INFECTED = optvals["INIT_FRAC_INFECTED"].as<double>();
  GLOBAL.INCUBATION_PERIOD = optvals["INCUBATION_PERIOD"].as<double>();
  GLOBAL.MEAN_ASYMPTOMATIC_PERIOD = optvals["MEAN_ASYMPTOMATIC_PERIOD"].as<double>();
  GLOBAL.MEAN_SYMPTOMATIC_PERIOD = optvals["MEAN_SYMPTOMATIC_PERIOD"].as<double>();
  GLOBAL.SYMPTOMATIC_FRACTION = optvals["SYMPTOMATIC_FRACTION"].as<double>();
  GLOBAL.MEAN_HOSPITAL_REGULAR_PERIOD = optvals["MEAN_HOSPITAL_REGULAR_PERIOD"].as<double>();
  GLOBAL.MEAN_HOSPITAL_CRITICAL_PERIOD = optvals["MEAN_HOSPITAL_CRITICAL_PERIOD"].as<double>();
  GLOBAL.COMPLIANCE_PROBABILITY = optvals["COMPLIANCE_PROBABILITY"].as<double>();

  GLOBAL.BETA_H = optvals["BETA_H"].as<double>();
  GLOBAL.BETA_W = optvals["BETA_W"].as<double>();
  GLOBAL.BETA_C = optvals["BETA_C"].as<double>();
  GLOBAL.BETA_S = optvals["BETA_S"].as<double>();
  GLOBAL.BETA_TRAVEL = optvals["BETA_TRAVEL"].as<double>();

  GLOBAL.HD_AREA_FACTOR = optvals["HD_AREA_FACTOR"].as<double>();
  GLOBAL.HD_AREA_EXPONENT = optvals["HD_AREA_EXPONENT"].as<double>();
  
  GLOBAL.INTERVENTION
	= static_cast<Intervention>(optvals["INTERVENTION"].as<count_type>());
  
  GLOBAL.CALIBRATION_DELAY = optvals["CALIBRATION_DELAY"].as<double>();
  GLOBAL.DAYS_BEFORE_LOCKDOWN = optvals["DAYS_BEFORE_LOCKDOWN"].as<double>();
  GLOBAL.NUM_DAYS_BEFORE_INTERVENTIONS = GLOBAL.CALIBRATION_DELAY + GLOBAL.DAYS_BEFORE_LOCKDOWN;

  std::string output_dir(optvals["output_directory"].as<std::string>());

  GLOBAL.input_base = optvals["input_directory"].as<std::string>();
  //Done saving options
  
  //Compute parametrs based on options
  GLOBAL.NUM_TIMESTEPS = GLOBAL.NUM_DAYS*GLOBAL.SIM_STEPS_PER_DAY;
  GLOBAL.INCUBATION_PERIOD_SCALE = GLOBAL.INCUBATION_PERIOD*GLOBAL.SIM_STEPS_PER_DAY;

  GLOBAL.ASYMPTOMATIC_PERIOD = GLOBAL.MEAN_ASYMPTOMATIC_PERIOD*GLOBAL.SIM_STEPS_PER_DAY;
  GLOBAL.SYMPTOMATIC_PERIOD = GLOBAL.MEAN_SYMPTOMATIC_PERIOD*GLOBAL.SIM_STEPS_PER_DAY;
  GLOBAL.HOSPITAL_REGULAR_PERIOD = GLOBAL.MEAN_HOSPITAL_REGULAR_PERIOD*GLOBAL.SIM_STEPS_PER_DAY;
  GLOBAL.HOSPITAL_CRITICAL_PERIOD = GLOBAL.MEAN_HOSPITAL_CRITICAL_PERIOD*GLOBAL.SIM_STEPS_PER_DAY;

  
  if(GLOBAL.input_base != ""
	 && GLOBAL.input_base[GLOBAL.input_base.size() - 1] != '/'){ 
	GLOBAL.input_base += '/';
	//Make sure the path of the input_base
	//directory is terminated by a "/"
  }

  //Initialize output folders
  gnuplot gnuplot(output_dir);

  //Run simulations
  auto plot_data = run_simulation();

  //Start output
  output_global_params(output_dir);

  for(const auto& elem: plot_data){
	std::string csvfile_name = elem.first + ".csv";
	std::string csvfile_path = output_dir + "/" + csvfile_name;
	if(elem.first == "csvContent"){
	  //This file contains everything!
	  output_timed_csv({"community",
						"infected",
						"affected",
						"hospitalised",
						"critical",
						"dead",
						"hd_area_affected"},
		csvfile_path, elem.second);
	} else {
	  output_timed_csv({elem.first},
					   csvfile_path,
					   elem.second);
	  gnuplot.plot_data(elem.first);
	}
  }
  return 0;
}
