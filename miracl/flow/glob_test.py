import argparse
from pathlib import Path

# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# Add the --dir flag to the parser
parser.add_argument("--wild_dir", type=Path, help="Path to base wild directory")
parser.add_argument("--wild_tiffs", type=Path, help="Path to wild tiff directory")
parser.add_argument("--disease_dir", type=Path, help="Path to base disease directory")
parser.add_argument("--disease_tiffs", type=Path, help="Path to disease tiff directory")

# Parse the arguments
args = parser.parse_args()


def get_dir_paths(dir_var, tiffs_var):
    # Get the subdirectories within the provided directory
    subdirectories = [subdir for subdir in dir_var.iterdir() if subdir.is_dir()]

    # Filter for the 'cells' subdirectories
    cells_directories = [
        subdir / tiffs_var for subdir in subdirectories if (subdir / tiffs_var).is_dir()
    ]

    return cells_directories


def do_sth(dir_list):
    for i in dir_list:
        print(i)


def main(args):
    # Assign tiff dir str
    wild_dir = args.wild_dir
    wild_tiffs = args.wild_tiffs
    disease_dir = args.disease_dir
    disease_tiffs = args.disease_tiffs

    # Get dir lists
    wild_dirs, disease_dirs = get_dir_paths(wild_dir, wild_tiffs), get_dir_paths(
        disease_dir, disease_tiffs
    )

    # Run analysis
    do_sth(wild_dirs)
    do_sth(disease_dirs)


if __name__ == "__main__":
    main(args)
