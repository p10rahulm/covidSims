#ifndef OUTPUTS_H_
#define OUTPUTS_H_
#include "models.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <string>

void output_timed_csv(const std::vector<std::string>& field_row, const std::string& output_file, const matrix<count_type>& mat);

void output_global_params(const std::string& filename);

struct gnuplot{
public:
  gnuplot(const std::string& output_directory);
  void plot_data(const std::string& name);
  ~gnuplot();
  
private:
  std::ofstream fout;
  std::ofstream html_out;
};

void check_stream(const std::ofstream& fout, const std::string& path);

#endif
