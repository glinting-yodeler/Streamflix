from src.seed_dimensions import main as seed_dimensions
from src.clean_events import main as clean_events
from src.build_marts import main as build_marts
from src.train_churn import main as train_churn
from src.recommend import main as recommend
from src.genai_summary import main as genai_summary


def main():
    print("1/6 Seeding dimensions...")
    seed_dimensions()
    print("2/6 Cleaning raw events...")
    clean_events()
    print("3/6 Building analytics marts...")
    build_marts()
    print("4/6 Training churn model...")
    train_churn()
    print("5/6 Generating recommendations...")
    recommend()
    print("6/6 Generating executive summary...")
    genai_summary()
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
