import pandas, matplotlib
from collections import defaultdict
from pathlib import Path
import sys

output_base = sys.argv[1]
INTERVENTION_NOS = 7

interventions = {
    0: "no_intervention",
    1: "case_isolation",
    2: "home_quarantine",
    3: "lockdown",
    4: "case_isolation_and_home_quarantine",
    5: "case_isolation_and_home_quarantine_sd_70_plus",
    6: "lockdown_21_ci_hq_sd_70_plus_21_ci",
    7: "lockdown_21"
}

var_names = [
    "num_infected",
    "num_exposed",
    "num_hospitalised",
    "num_critical",
    "num_fatalities",
    "num_recovered",
    "num_affected",
]

derived_var_names = ["case_fatality_ratio"];

dfs = defaultdict(list)

for INTERVENTION in range(0, INTERVENTION_NOS + 1):
    # variables read from files
    for var_name in var_names:
        dfs[var_name].append(pandas.read_csv(Path(output_base, f"intervention_{INTERVENTION}", f"{var_name}.csv")))

    #derived variables
    dfs["case_fatality_ratio"].append(
        dfs["num_fatalities"][INTERVENTION].rename(
            columns = {"num_fatalities": "case_fatality_ratio"}
        )
    )
    dfs["case_fatality_ratio"][INTERVENTION]["case_fatality_ratio"] = (
        dfs["case_fatality_ratio"][INTERVENTION]["case_fatality_ratio"] /
        dfs["num_affected"][INTERVENTION]["num_affected"]
    )




html_out = open(Path(output_base, "plots.html"), "w")
print("<html>\n"
      "<head><title>Plots: All interventions</title></head>\n"
      "<body>\n"
      "  <h1>All interventions</h1>\n",
      "  <table>\n",
      file = html_out
)

for key in range(0, INTERVENTION_NOS + 1):
    print(f"<tr><td>{key}</td>\n",
          f"    <td>{interventions[key]}</td>\n",
          f"</tr>", file = html_out)
    

print("  </table>\n", file = html_out)
      


for var_name in var_names + derived_var_names:
    df = dfs[var_name][0];
    df.rename(columns={var_name: str(0)}, inplace = True)
    for i in range(1, 8):
        df[str(i)] = dfs[var_name][i][var_name]

    ax = df.plot(x = "Time", title = var_name)
    image_name =  f"{var_name}.png"
    output_path = Path(output_base, image_name)
    print(f"Saving {var_name} plot in {output_path}", flush=True)
    ax.figure.savefig(output_path)
    print("<p><img src=\"" + image_name + "\">\n",
        file=html_out)

html_out.close()


