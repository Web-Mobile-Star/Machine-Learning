import argparse
import pandas as pd
import requests


def main(data_frame_path: str, model_uri: str):
    df = pd.read_csv(data_frame_path)
    for entry in df.to_dict(orient="records")[1:]:
        response = requests.post(
            model_uri, json=entry, headers={"content-type": "application/json"}
        )
        print(response.status_code)
        print(response.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_frame_path", type=str)
    parser.add_argument("model_uri", type=str)

    args, _ = parser.parse_known_args()

    main(args.data_frame_path, args.model_uri)
