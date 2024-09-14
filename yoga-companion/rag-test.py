#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
import minsearch
from openai import OpenAI
from tqdm.auto import tqdm
import random
import json


# Ingestion

# download minsearch
if not os.path.exists('minsearch.py'):
    # Download only if minsearch.py does not exist
    get_ipython().system('wget https://raw.githubusercontent.com/alexeygrigorev/minsearch/main/minsearch.py')
else:
    print("File already exists.")

# Load the data and display the first few rows
data = pd.read_csv('/workspaces/fitness-assistant-rag/data/yoga_poses.csv')
data.head()

# Convert the data to a list of dictionaries
documents = data.to_dict(orient='records')

# Create an index for the search engine
index = minsearch.Index(
    text_fields=['pose_name', 'type_of_practice', 'variation', 'position',
       'difficulty', 'props_required', 'body_focus', 'benefits',
       'instructions'],
    keyword_fields=['id']
)

# Add the documents to the index
index.fit(documents)


# RAG Flow

# Connect to OpenAI
client = OpenAI()

def search(query):
    boost = {}

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )

    return results

prompt_template = """
You are a yoga guru with access to a comprehensive yoga poses database. Answer the QUESTION using only the information provided in the CONTEXT.
Treat similar words as synonyms and recognize variations of terms as equivalent.
Be concise, avoid repetition, and strictly adhere to the CONTEXT. 
If there are variations of the pose in the CONTEXT, tell the user about it.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

entry_template = """
Pose: {pose_name}
Practice: {type_of_practice}
Variation: {variation}
Position: {position}
Difficulty: {difficulty}
Props: {props_required}
Focus: {body_focus}
Benefits: {benefits}
Instructions: {instructions}
""".strip()

def build_prompt(query, search_results):
    context = "\n\n".join([entry_template.format(**doc) for doc in search_results])
    return prompt_template.format(question=query, context=context)

def llm(prompt, model='gpt-4o-mini'):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def rag(query, model='gpt-4o-mini'):
    search_results = search(query)
    prompt = build_prompt(query, search_results)
    #print(prompt)
    answer = llm(prompt, model=model)
    return answer


# In[12]:


question = "How do I perform the variation of Warrior I with a block?"
answer = rag(question)
print(answer)


# ### Retrieval Evaluation

# In[13]:


data_question = pd.read_csv('../data/ground-truth-retrieval.csv')


# In[14]:


data_question.head()


# In[15]:


ground_truth = data_question.to_dict(orient='records')


# In[16]:


ground_truth[0]


# In[17]:


def hit_rate(relevance_total):
    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt = cnt + 1

    return cnt / len(relevance_total)

def mrr(relevance_total):
    total_score = 0.0

    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] == True:
                total_score = total_score + 1 / (rank + 1)

    return total_score / len(relevance_total)


# In[18]:


def minsearch_search(query):
    boost = {}

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )

    return results


# In[19]:


def evaluate(ground_truth, search_function):
    relevance_total = []

    for q in tqdm(ground_truth):
        doc_id = q['id']
        results = search_function(q)
        relevance = [d['id'] == doc_id for d in results]
        relevance_total.append(relevance)

    return {
        'hit_rate': hit_rate(relevance_total),
        'mrr': mrr(relevance_total),
    }


# In[20]:


evaluate(ground_truth, lambda q: minsearch_search(q['question']))


# ### Finding the best paramenters

# In[31]:


data_validation = data_question[:360]
data_test = data_question[360:]


# In[32]:


def simple_optimize(param_ranges, objective_function, n_iterations=10):
    best_params = None
    best_score = float('-inf')  # Assuming we're minimizing. Use float('-inf') if maximizing.

    for _ in range(n_iterations):
        # Generate random parameters
        current_params = {}
        for param, (min_val, max_val) in param_ranges.items():
            if isinstance(min_val, int) and isinstance(max_val, int):
                current_params[param] = random.randint(min_val, max_val)
            else:
                current_params[param] = random.uniform(min_val, max_val)
        
        # Evaluate the objective function
        current_score = objective_function(current_params)
        
        # Update best if current is better
        if current_score > best_score:  # Change to > if maximizing
            best_score = current_score
            best_params = current_params
    
    return best_params, best_score


# In[33]:


gt_val = data_validation.to_dict(orient='records')


# In[34]:


def minsearch_search(query, boost=None):
    if boost is None:
        boost = {}

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )

    return results


# In[35]:


param_ranges = {
    'pose_name': (0.0, 3.0),
    'type_of_practice': (0.0, 3.0),
    'variation': (0.0, 3.0),
    'position': (0.0, 3.0),
    'difficulty': (0.0, 3.0),
    'props_required': (0.0, 3.0),
    'body_focus': (0.0, 3.0),
    'benefits': (0.0, 3.0),
    'synonyms': (0.0, 3.0),
    'instructions': (0.0, 3.0),
    'context': (0.0, 3.0)
}

def objective(boost_params):
    def search_function(q):
        return minsearch_search(q['question'], boost_params)

    results = evaluate(gt_val, search_function)
    return results['mrr']


# In[36]:


simple_optimize(param_ranges, objective, n_iterations=25)


# In[37]:


def minsearch_improved(query):
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

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )

    return results

evaluate(ground_truth, lambda q: minsearch_improved(q['question']))


# In[38]:


prompt2_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer_llm}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()


# In[39]:


len(ground_truth)


# In[40]:


record = ground_truth[0]
question = record['question']
answer_llm = rag(question)


# In[41]:


prompt = prompt2_template.format(question=question, answer_llm=answer_llm)
print(prompt)


# In[42]:


data_sample = data_question.sample(n=200, random_state=1)


# In[43]:


sample = data_sample.to_dict(orient='records')


# In[45]:


evaluations = []

for record in tqdm(sample):
    question = record['question']
    answer_llm = rag(question) 

    prompt = prompt2_template.format(
        question=question,
        answer_llm=answer_llm
    )

    evaluation = llm(prompt)
    evaluation = json.loads(evaluation)

    evaluations.append((record, answer_llm, evaluation))


# In[46]:


data_eval = pd.DataFrame(evaluations, columns=['record', 'answer', 'evaluation'])

data_eval['id'] = data_eval.record.apply(lambda d: d['id'])
data_eval['question'] = data_eval.record.apply(lambda d: d['question'])

data_eval['relevance'] = data_eval.evaluation.apply(lambda d: d['Relevance'])
data_eval['explanation'] = data_eval.evaluation.apply(lambda d: d['Explanation'])

del data_eval['record']
del data_eval['evaluation']


# In[48]:


data_eval.relevance.value_counts()


# In[47]:


data_eval.relevance.value_counts(normalize=True)


# In[49]:


data_eval.to_csv('../data/rag-eval-gpt-4o-mini.csv', index=False)


# In[50]:


data_eval[data_eval.relevance == 'NON_RELEVANT']


# In[51]:


evaluations_gpt4o = []

for record in tqdm(sample):
    question = record['question']
    answer_llm = rag(question, model='gpt-4o') 

    prompt = prompt2_template.format(
        question=question,
        answer_llm=answer_llm
    )

    evaluation = llm(prompt)
    evaluation = json.loads(evaluation)
    
    evaluations_gpt4o.append((record, answer_llm, evaluation))


# In[52]:


data_eval = pd.DataFrame(evaluations_gpt4o, columns=['record', 'answer', 'evaluation'])

data_eval['id'] = data_eval.record.apply(lambda d: d['id'])
data_eval['question'] = data_eval.record.apply(lambda d: d['question'])

data_eval['relevance'] = data_eval.evaluation.apply(lambda d: d['Relevance'])
data_eval['explanation'] = data_eval.evaluation.apply(lambda d: d['Explanation'])

del data_eval['record']
del data_eval['evaluation']


# In[53]:


data_eval.relevance.value_counts()


# In[54]:


data_eval.relevance.value_counts(normalize=True)


# In[55]:


data_eval.to_csv('../data/rag-eval-gpt-4o.csv', index=False)

