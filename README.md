# Yoga Companion RAG Application

#### Maintaining a regular yoga practice can be challenging, especially for beginners. Studios can be intimidating, and personal instructors aren't always accessible or affordable. The AI Yoga Assistant provides a conversational AI that helps users choose yoga poses, find modifications, and create personalized sequences, making yoga more approachable and manageable for practitioners of all levels.

## Techologies
* Python 3.12
* Docker and Docker Compose for containerization
* Minsearch for full-text search
* Flask as the API interface 
* Grafana for monitoring and PostgreSQL as the backend for it
* OpenAI as an LLM

## Intructions to run the application

Installing dependencies

```bash
pipenv install
```

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