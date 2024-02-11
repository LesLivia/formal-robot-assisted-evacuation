Towards Verified Robot-Controlled SaR Scenarios
===============================================

The repository contains a tool to generate and simulate formally verified strategies for Search-and-Rescue (SaR) robots in evacuation scenarios.

The tool builds upon the work presented in [1][paper1].

Authors:

| Name                    | E-mail address           |
|:------------------------|:-------------------------|
| Gavidia-Calderon Carlos | cgavidiac@gmail.com      |
| Lestingi Livia          | livia.lestingi@polimi.it |

Project Structure
-----------

The tool generates an [Uppaal Stratego model](stratego_generator/it/polimi/mgrs/model_mgr.py) based on [input parameters](stratego_generator/it/polimi/mgrs/param_mgr.py).

An [Uppaal Stratego][stratego] experiment is then to [generate](stratego_generator/it/polimi/mgrs/strategy_mgr.py) a verified and optimal strategy for the SaR robot. 

The generated strategy is then [converted](stratego_generator/it/polimi/mgrs/code_mgr.py) into an executable Python script invoked at runtime by the [simulator](impact2.10.7) to get the best decision based on the current state of the system. 


Configuration File Setup
-----------

The tool requires a [configuration file](stratego_generator/resources/config/config.ini) whose content must be adjusted to match your
environment. Make sure that the following properties match your environment:

- **UPPAAL_PATH** is the path to Uppaal *verifyta* executable

Python Dependencies
-----------

Install the required dependencies:

	pip install -r $REPO_PATH/requirements.txt

Add the repo path to your Python path (fixes ModuleNotFoundError while trying to execute from command line):

	export PYTHONPATH="${PYTHONPATH}:$REPO_PATH"

Initialize Git submodules with:

	git submodule init
	git submodule update

---

*Copyright &copy; 2024 Carlos Gavidia-Calderon, Livia Lestingi*

[paper1]: https://doi.org/10.1145/3510455.3512791

[uppaal]: https://uppaal.org/

[stratego]: https://people.cs.aau.dk/~marius/stratego/