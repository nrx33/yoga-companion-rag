# import the necessary packages
from openai import OpenAI
import ingest

# Connect to OpenAI
client = OpenAI()

# Load the index
index = ingest.load_index()

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
Be very concise, avoid repetition, and strictly adhere to the CONTEXT. 
If there are variations of the pose in the CONTEXT, tell the user about it.
If you cant answer something just say you cant answer that question.
If no context or information is provided do not mention that something or context or what is not provided.
Talk in enthusiastic tone and anything related to yoga you can talk about it.


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
