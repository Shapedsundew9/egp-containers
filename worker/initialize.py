"""Initializes the worker python execution environment."""
from argparse import ArgumentParser, Namespace
from json import load, dump
from logging import Logger, NullHandler, getLogger
from os import W_OK, access
from os.path import exists, join
from pathlib import Path
from sys import exit as sys_exit
from typing import Any, Iterator, cast

from egp_population.population_config import population_table_default_config, configure_populations
from egp_population.egp_typing import PopulationConfigNorm
from egp_stores.egp_typing import GenePoolConfigNorm
from egp_stores.gene_pool import default_config as gp_default_config
from egp_worker.config_validator import dump_config, load_config
from egp_worker.egp_typing import WorkerConfigNorm
from pypgtable import table
from pypgtable.pypgtable_typing import TableConfigNorm
from requests import Response, get

_logger: Logger = getLogger(__name__)
_logger.addHandler(NullHandler())


parser: ArgumentParser = ArgumentParser(prog="egp-worker")
parser.add_argument("--config_file", "-c", "Path to a JSON configuration file.")
parser.add_argument(
    "--default_config",
    "-d",
    "Generate a default configuration file. config.json will be stored in the current directory. All other options ignored.",
    action="store_true",
)
parser.add_argument(
    "--update",
    "-U",
    "Update Erasmus GP before starting worker process.",
    action="store_true",
)
args: Namespace = parser.parse_args()

# Save the default config
if args.default_config:
    dump_config()
    sys_exit(0)

# Load the config file
config: WorkerConfigNorm = load_config(args.config_file)

# Check the problem data folder
directory_path: str = config["problem_folder"]
if exists(directory_path):
    if not access(directory_path, W_OK):
        print(f"The 'problem_folder' directory '{directory_path}' exists but is not writable.")
        sys_exit(1)
else:
    # Create the directory if it does not exist
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        print(f"The 'problem_folder' directory '{directory_path}' does not exist and cannot be created: {e}")
        sys_exit(1)

# Check the verified problem definitions file
problem_definitions: list[dict[str, Any]] = []
problem_definitions_file: str = join(directory_path, 'egp_problems.json')
problem_definitions_file_exists: bool = exists(problem_definitions_file)
if not problem_definitions_file_exists:
    _logger.info(f"The egp_problems.json does not exist in {directory_path}'. Pulling from {config['problem_definitions']}")
    response: Response = get(config['problem_definitions'], timeout=30)
    if (problem_definitions_file_exists := response.status_code == 200):
        with open(problem_definitions_file, "wb") as file:
            file.write(response.content)
        _logger.info("File 'egp_problems.json' downloaded successfully.")
    else:
        _logger.warning(f"Failed to download the file. Status code: {response.status_code}.")

# Load the problems definitions file if it exists
if problem_definitions_file_exists:
    with open(problem_definitions_file, "r", encoding="utf8") as file_ptr:
        problem_definitions = load(file_ptr)

# Define gene pool configuration
gp_config: GenePoolConfigNorm = gp_default_config()
base_name: str = config["gene_pool"]["table"]
for key, table_config in cast(Iterator[tuple[str, TableConfigNorm]], gp_config.items()):
    table_config["table"] = config["gene_pool"]["table"] if key == "gene_pool" else config["gene_pool"]["table"] + "_" + key
    table_config["database"] = config["databases"][config["gene_pool"]["database"]]

# Define population configuration
# The population configuration is persisted in the gene pool database
p_table_config: TableConfigNorm = population_table_default_config()
p_table_config["table"] = gp_config["gene_pool"]["table"] + "_populations"
p_table_config["database"] = gp_config["gene_pool"]["database"]

# Dump the populations defined for the gene pool
if args.population_list:
    p_table_config["create_db"] = False
    p_table_config["create_table"] = False
    p_table: table = table(p_table_config)
    config["population"]["configs"] = list(p_table.select())
    with open("config.json", "w", encoding="utf8") as file_ptr:
        dump(config, file_ptr, indent=4, sort_keys=True)
    print("Configuration updated with Gene Pool population configurations written to ./config.json")
    sys_exit(0)

# Get the population configurations
p_config_tuple: tuple[dict[int, PopulationConfigNorm], table, table] = configure_populations(
    config["population"], problem_definitions, p_table_config)
p_configs: dict[int, PopulationConfigNorm] = p_config_tuple[0]
p_table: table = p_config_tuple[1]
pm_table: table = p_config_tuple[2]
