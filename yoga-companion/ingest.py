# import the necessary libraries
import minsearch
import pandas as pd
import os

DATA_PATH = os.getenv("DATA_PATH", "../data/yoga_poses.csv")


def load_index(data_path=DATA_PATH):
    # Load the data
    data = pd.read_csv(data_path)

    # Convert the data to a list of dictionaries
    documents = data.to_dict(orient="records")

    # Create an index for the search engine
    index = minsearch.Index(
        text_fields=[
            "pose_name",
            "type_of_practice",
            "variation",
            "position",
            "difficulty",
            "props_required",
            "body_focus",
            "benefits",
            "instructions",
        ],
        keyword_fields=["id"],
    )

    # Add the documents to the index
    index.fit(documents)
    return index
