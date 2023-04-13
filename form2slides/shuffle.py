from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
import random

with open("token.pickle", "rb") as file:
    creds = pickle.load(file)

slides_service = build("slides", "v1", credentials=creds)

# presentation_id = "15Z6SH8QjYatn3tgNeKZ-ZVyYqDuyn09nTzyPyVuRjZI" # test
presentation_id = "1CzdyPM6fOlPWT_by0177xS_nXzPy7LciUixj8FlZlxM"  # prod

# Get the list of slide IDs in the presentation
presentation = (
    slides_service.presentations().get(presentationId=presentation_id).execute()
)
slides = presentation.get("slides")[1:]  # skip title slide
slide_ids = [slide["objectId"] for slide in slides]

# Shuffle the list of slide IDs
random.shuffle(slide_ids)

# Update the slide order in the presentation
requests = [
    {"updateSlidesPosition": {"slideObjectIds": [slide_id], "insertionIndex": i}}
    for i, slide_id in enumerate(slide_ids, 1)  # skip ix 0 to preserve title slide
]

# Execute the batch update request to update the slide order
slides_service.presentations().batchUpdate(
    presentationId=presentation_id, body={"requests": requests}
).execute()
