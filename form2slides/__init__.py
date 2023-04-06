from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
import uuid

with open("token.pickle", "rb") as file:
    creds = pickle.load(file)

# Initialize the Google Form and Slides APIs
form_service = build("forms", "v1", credentials=creds)
slides_service = build("slides", "v1", credentials=creds)

# Get Google Form responses
form_id = "1dHdspfMBU1kM5hgQ9j4cTFGaeInH9V4H4RGweaEyO7w"
form = form_service.forms().get(formId=form_id).execute()
responses = (
    form_service.forms().responses().list(formId=form_id).execute().get("responses", [])
)

# print([x.get("title", "") for x in form["items"]])
question_to_id = {
    "Имя": "",
    "Телеграм-ник": "",
    "Работаю здесь и занимаюсь этим:": "",
    "Био:": "",
    "Ключевые слова": "",
    "Личная страничка / GitHub": "",
}

# print(form["items"])

for item in form["items"]:
    if item.get("title", "NA") in question_to_id.keys():
        question_to_id[item["title"]] = item["questionItem"]["question"]["questionId"]


# Generate slides from form responses
def process_response(response):
    id_to_answer = response["answers"]

    return {
        question_name: id_to_answer[question_id]["textAnswers"]["answers"][0]["value"]
        if question_id in id_to_answer
        else None
        for question_name, question_id in question_to_id.items()
    }


participants = [process_response(response) for response in responses]

### Create slides from responses

presentation_id = "15Z6SH8QjYatn3tgNeKZ-ZVyYqDuyn09nTzyPyVuRjZI"

# templates = (
#     slides_service.presentations()
#     .get(presentationId=presentation_id)
#     .execute()
#     .get("layouts")
# )

# # Print the layoutId for each slide layout
# for layout in templates:
#     print(layout["objectId"], layout["layoutProperties"]["name"])

for participant in participants:
    # Define the request to create the new slide using the specified template and page elements
    ids = [uuid.uuid4().hex for _ in range(5)]
    requests = [
        {
            "createSlide": {
                "slideLayoutReference": {"layoutId": "g22bc2b6b380_0_0"},
                "placeholderIdMappings": [
                    {
                        "layoutPlaceholder": {"type": "TITLE", "index": 0},
                        "objectId": ids[0],
                    },
                    {
                        "layoutPlaceholder": {"type": "SUBTITLE", "index": 0},
                        "objectId": ids[1],
                    },
                    {
                        "layoutPlaceholder": {"type": "BODY", "index": 0},
                        "objectId": ids[2],
                    },
                    {
                        "layoutPlaceholder": {"type": "BODY", "index": 1},
                        "objectId": ids[3],
                    },
                    {
                        "layoutPlaceholder": {"type": "BODY", "index": 2},
                        "objectId": ids[4],
                    },
                ],
            }
        },
        {
            "insertText": {
                "objectId": ids[0],
                "text": participant["Имя"],
            }
        },
        {
            "insertText": {
                "objectId": ids[1],
                "text": participant["Работаю здесь и занимаюсь этим:"],
            }
        },
        {
            "insertText": {
                "objectId": ids[2],
                "text": participant["Био:"],
            }
        },
        {
            "insertText": {
                "objectId": ids[3],
                "text": participant["Ключевые слова"],
            }
        },
        {
            "insertText": {
                "objectId": ids[4],
                "text": participant["Телеграм-ник"],
            }
        },
    ]

    # Execute the request to create the new slide
    response = (
        slides_service.presentations()
        .batchUpdate(presentationId=presentation_id, body={"requests": requests})
        .execute()
    )

    # Print the ID of the newly created slide
    print(response["replies"][0]["createSlide"]["objectId"])
