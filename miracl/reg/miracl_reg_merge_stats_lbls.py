import pandas as pd
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Merge extracted region stats with atlas labels."
    )
    parser.add_argument(
        "--extracted", type=Path, required=True, help="Path to extracted TSV file"
    )
    parser.add_argument(
        "--labels", type=Path, required=True, help="Path to label CSV file"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="Path to output CSV file"
    )

    args = parser.parse_args()

    extracted = pd.read_csv(args.extracted, sep=r"\s+", engine="python")
    labels = pd.read_csv(args.labels)

    merged = pd.merge(
        extracted,
        labels,
        left_on="Label",
        right_on="idx",
        how="inner",
    )

    merged = merged.drop(columns=["idx"]).rename(
        columns={
            "Label": "label_idx",
            **{col: col.replace("%", "percentile") for col in merged.columns},
        }
    )
    merged.columns = [col.strip().lower() for col in merged.columns]

    merged.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
