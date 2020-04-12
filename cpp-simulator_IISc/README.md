To run the simulator, you need:

1. a recent version of the `g++` compiler (6.1 or later) or `clang` (I
think 4 or later works, but have not tested), and optionally `openmp`
(this is to enable parallelization, and can be disabled easily, see
below in the compiling section if your compiler does not have it),

2. The `make` program.

3. The `bash` shell.

4. The `gnuplot` program for generating some of the plots.

5. `python` pointing to a `python3` executable with `matplotlib` and
   `pandas` installed, in your execution `PATH`. (Otherwise, you will
   have to edit the `python` invocation in the shell script to point
   to such a `python3` installation.)

On windows, the easiest way to get these is to install `msys2` shell
from [here](https://www.msys2.org/).  However, it may be tricky to get
an MSYS installation with a `python3` capable of installing `pandas`.
You might then have to point `MSYS` to actually use your Windows
`python3` installation. Let me know if you need help.

On Mac and Linux, these programs are typically already there, or else
are easy to install with a package manager.


## Compiling the code

You can now compile the code in the `cpp_simulator` directory by running:

```
make all
```

However, if you do not want to use, or do not have, the `openmp`
parallel libraries, you should instead run

```
make -f Makefile_np all
```


This will generate an executable file called `drive_simulator` in the
same directory.


## Running the code

Now  to actually run the code, you will have to edit the file
`drive_simulator_temp.sh` in the same directory.  Here, you can specify

1) All the input parameters.

2) The directory where the output will be generated (The
	`output_directory_base` parameter in the file).  This option can
	also be passed to the script from the command line as shown below.

3) The directory in which the input files reside. (The
	`input_directory` parameter in the file.)  This option can also be
	passed to the script from the command line as shown below.

Once you have fixed the prameters, you can run the script as

```
bash drive_simulator_temp.sh [-i input_directory] [-o output_directory_base]
```

in the `cpp-simulator` directory.  If everything works, it will end
with a message indicating success after a little while (~25s per
intervention on my computer with 1,00,000 agents).

The main simulator executable is in `drive_simulator`.  It runs for a
single intervention stratey, and all the parameters can be specfied on
the command line via named arguments (this is the program called by
the `drive_simulator_temp.sh` script above).  To see the option you
can run the following command in the the `cpp-simulator` directory:

```
./drive_simulator -h
```

## Viewing the output

The output can now be seen by using your favorite browser to open the
`plots.html` files in the output directories.

	- There will be one ouput directory per intervention (inside the directory you specified), containing the plots just for that intervention.
	- In addition, in the top level directory (the one you specified)q with plots which plot the observable variables for all the interventions on the same plot.

The per intervention directories also have the raw CSV files from
which the plots are generated.

