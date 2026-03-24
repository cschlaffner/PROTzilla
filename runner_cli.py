import argparse
import sys
from pathlib import Path

# import project path because module is not found
project_root_path = Path(__file__).parent.parent
sys.path.append(str(project_root_path))

from backend.protzilla.runner import Runner


def args_parser():
    parser = argparse.ArgumentParser(
        argument_default=None,
        description="Command line tool to execute a saved PROTzilla workflow using a file-input mapping.",
        prog="PROTzilla Runner",
        epilog="Thanks for using PROTzilla! :)",
    )

    # paths to files have to be supplied in quotes on the command line
    parser.add_argument(
        "workflow",
        action="store",
        help="name of a workflow, saved in /user_data/workflows",
    )
    parser.add_argument(
        "file_input_map",
        metavar="file-input-map",
        action="store",
        help="path to a YAML file using step_id -> {field_name: path}",
    )
    parser.add_argument(
        "--msfragger-path",
        action="store",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--diann-path",
        action="store",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--diann-meta-data-path",
        action="store",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--meta-data-path",
        action="store",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--peptides-path",
        action="store",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--evidence-path",
        action="store",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--fasta-path",
        action="store",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-n",
        "--run-name",
        action="store",
        help="Name of the run. If not provided a random name will be assigned",
    )
    # parser.add_argument("-d", "--df-mode", action="store", help="disk or memory") # Doenst work according to Joris, so we dont want this in the release. Standard is currently disk.
    parser.add_argument(
        "-p",
        "--all-plots",
        action="store_true",
        help="create all plots and save them to backend/user_data/runs/<runName>/plots, default: false",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="when provided, all Parsed Arguments will be shown",
    )
    return parser


def main(raw_args):
    parser = args_parser()
    kwargs = parser.parse_args(raw_args).__dict__
    runner = Runner(**kwargs)
    runner.compute_workflow()


if __name__ == "__main__":
    main(sys.argv[1:])
