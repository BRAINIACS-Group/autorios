# autorios

This is a GUI automation tool for the TA Instruments Trios rheometer control software.
It is primarily focused on running continuous large strain measurements for the mechanical characterization of solids. It enables you to combine several procedure files into one experimental run and synchronize Trios with the ARG2AuxiliarySample.exe application (called the "datalogger" in the rest of this document).

The combination with the datalogger proved especially valuable in our experiments, as it must be manually started during an experiment and cannot run in parallel with frequency sweep measurements.

# Build and install

## Install as a Python package via pip
```
pip install . 
```
For system-wide installations [pipx](https://pipx.pypa.io/stable/) is recommended.
```
pipx install .
```

## Build a Windows executable
We use [hatch-pyinstaller](https://github.com/mxysptlk/hatch-pyinstaller) to build an executable with [pyinstaller](https://pyinstaller.org/en/stable/).
```
hatch build --target pyinstaller
```
The autorios executable can then be found in the created dist folder.

# Run

First, you need to start the Trios software so autorios can connect to it.

If you installed the Windows executable, you can run it directly.

If you installed Autorios as a Python package, you can start it via:
```
python -m autorios
```

# Protocol Configuration

Experiments are defined via protocol YAML files. Each protocol file can contain one or more procedure steps.

## Step Types

The following step types are supported:

- **GAP**: Sets the gap (distance between rheometer geometries) to a specimen-dependent value (e.g., `["Step Label", "gap", "0.85*{specimen.height}"]`)
- **VELOCITY**: Sets the compression velocity in µm/s (e.g., `["Step Label", "velocity", "40"]`)
- **WAIT_FOR_TEMPERATURE**: Toggles the "Wait For Temperature" checkbox in the Environmental Control group (e.g., `["Step Label", "wait_for_temperature", None]`)
- **MOTOR_ROTATION**: Superimposes motor rotation with a specified angle (e.g., `["Step Label", "motor_rotation", "45"]`)
- **SOAK_TIME**: Sets the soak (equilibration) time in seconds (e.g., `["Step Label", "soak_time", "60"]`)

All numeric steps support expressions using `{specimen.height}` for dynamic values based on specimen geometry.
