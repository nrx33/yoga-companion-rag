# Yoga Companion RAG Application

#### Maintaining a regular yoga practice can be challenging, especially for beginners. Studios can be intimidating, and personal instructors aren't always accessible or affordable. The AI Yoga Assistant provides a conversational AI that helps users choose yoga poses, find modifications, and create personalized sequences, making yoga more approachable and manageable for practitioners of all levels.

## Techologies
* [Minsearch](https://github.com/alexeygrigorev/minsearch) - for full text search 
* GPT 4o-Mini as an LLM
* Flask as the API interface
* Streamlit for creating the user interface
* Grafana for monitoring and PostgreSQL as the backend for it

## Intructions to run the application

Installing dependencies

```bash
pipenv install
```

## Flask
It's a web application framework for Python: we can easily create an endpoint for asking questions and use web clients (like curl or requests) for communicating with it.

In our case, we can send questions to http://localhost:5000/question.

For more information, [click here](https://flask.palletsprojects.com/en/3.0.x/)

## Testing API
When the application is running you can use `curl` for interacting with the API

```bash
URL=http://localhost:5000
QUESTION="How do I perform the variation of Warrior I with a block?"
DATA='{
    "question": "'${QUESTION}'"
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${DATA}" \
    ${URL}/question
```

You will see something like the following in the response

```bash
{
  "answer": "To perform the variation of Warrior I with a block:\n\n1. Kneel on the mat and sit back on your heels.\n2. Stretch your arms forward while lowering your chest towards the mat.\n3. Use the block for support as you relax into the pose, breathing deeply.\n\nThis variation focuses on the back and helps relieve stress, and it is often practiced in restorative sessions.",
  "conversation_id": "ba09fb04-1309-43ff-b761-11b0e1e42fee",
  "question": "How do I perform the variation of Warrior I with a block?"
}
```

Sending feedback

```bash
ID="ba09fb04-1309-43ff-b761-11b0e1e42fee"
URL=http://localhost:5000
FEEDBACK_DATA='{
    "conversation_id": "'${ID}'",
    "feedback": 1
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${FEEDBACK_DATA}" \
    ${URL}/feedback
```

After sending it, you'll receive the acknowledgement

```bash
{
  "message": "Feedback received for conversation ba09fb04-1309-43ff-b761-11b0e1e42fee: 1"
}
```

Alternatively, you can also use `requests` to send questions - use [test.py](yoga-companion/test.py) for the testing process. The output should look something like the following

```bash
$ python test.py 
question:  What are the primary benefits of practicing the Camel Pose, particularly in its reclining variation?
{'answer': 'The primary benefits of practicing the Camel Pose, particularly in its reclining variation, include:\n\n- **Increases energy**: This restorative option is designed to uplift and energize the body.\n- **Focus on core strength**: The pose emphasizes core engagement, making it beneficial for building strength in that area.\n\nThe reclining variation is specifically beneficial for grounding and relaxation, ideal during restorative sessions.', 'conversation_id': '04e1c93e-fc8e-470e-b6b5-28226ebc67f5', 'question': 'What are the primary benefits of practicing the Camel Pose, particularly in its reclining variation?'}
```

## Streamlit 
Streamlit is an open-source Python framework that allows you to create and share beautiful, interactive web applications for machine learning and data science projects with minimal code.

For more information, [Click Here](https://docs.streamlit.io/)

![user-interface](assets/user_interface_streamlit.png)

## Experiments
For experiments, we use Jupyter notebooks. They are in the notebooks folder.


We have the following notebooks:

* [`rag-test.ipynb`](notebooks/rag-test.ipynb): The RAG flow and evaluating the system.
* [`eval-data-gen.ipynb`](notebooks/eval-data-gen.ipynb): Generating the ground truth dataset for retrieval evaluation.

## Retrieval Evaluation
The basic approach - using minsearch without any boosting - gave the following metrics:
* Hit rate: 86.9%
* MRR: 52.5%

The improved version (with tuned boosting):
* Hit rate: 96% (+9.1%)
* MRR: 58.7% (+6.2%)

The best boosting parameters:
```python
boost = {
    'pose_name': 1.77295549488741,
    'type_of_practice': 1.7646875012919119,
    'variation': 0.39512555991207565,
    'position': 2.0631444783206327,
    'difficulty': 1.4963276491573105,
    'props_required': 0.2392338995716874,
    'body_focus': 1.0491245848640036,
    'benefits': 1.7364406525582377,
    'synonyms': 2.5022067788712308,
    'instructions': 0.49163944386874336,
    'context': 2.1715194651138052
}
```

## RAG flow evaluation
We used the LLM-as-a-Judge metric to evaluate the quality of our RAG flow.

For gpt-4o-mini, in a sample with 200 records, we had:
* 132 (66%) RELEVANT
* 63 (31.5%) PARTLY_RELEVANT
* 5 (2.5%) NON_RELEVANT

We also tested gpt-4o:
* 98 (49%) RELEVANT
* 80 (40%) PARTLY_RELEVANT
* 22 (11%) NON_RELEVANT

The difference is significant, so we opted for gpt-4o-mini due to efficiency and cost ratio.