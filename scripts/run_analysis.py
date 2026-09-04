from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from used_car_intelligence.pipeline import run

parser = ArgumentParser(description="Run used-car market analysis and price modeling.")
parser.add_argument("--input", type=Path, default=ROOT / "data" / "raw" / "used_cars.csv")
args = parser.parse_args()
if not args.input.exists():
    raise SystemExit("Raw data not found. Run `python scripts/download_data.py` first.")
summary = run(args.input, ROOT)
print(summary)
