#include <string>

struct defaults{
  std::string NUM_DAYS = "120";
  std::string INIT_FRAC_INFECTED = "0.0001";
  std::string INCUBATION_PERIOD = "2.25";
  std::string MEAN_ASYMPTOMATIC_PERIOD = "0.5";
  std::string MEAN_SYMPTOMATIC_PERIOD = "5";
  std::string SYMPTOMATIC_FRACTION = "0.67";
  std::string MEAN_HOSPITAL_REGULAR_PERIOD = "8";
  std::string MEAN_HOSPITAL_CRITICAL_PERIOD = "8";
  std::string COMPLIANCE_PROBABILITY = "0.9";
  std::string BETA_H = "0.47";
  std::string BETA_W = "0.94";
  std::string BETA_C = "0.47045";
  std::string BETA_S = "1.88";
  std::string BETA_TRAVEL = "10.0";
  std::string HD_AREA_FACTOR = "2.0";
  std::string HD_AREA_EXPONENT = "0";
  std::string INTERVENTION = "0";
  std::string output_dir = "outputs/test_output_timing";
  std::string input_base = "../simulator/input_files";
  std::string SEED_HD_AREA_POPULATION = "false";
  std::string CALIBRATION_DELAY = "0";
  std::string DAYS_BEFORE_LOCKDOWN = "0";
} DEFAULTS;
