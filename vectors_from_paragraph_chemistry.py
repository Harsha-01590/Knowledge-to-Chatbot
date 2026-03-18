import openai
import csv
import sys
import os
import re

API_BASE_URL = "https://llama8b.gaia.domains/v1"
MODEL_NAME = "llama"
API_KEY = "gaia-NjhkMGM2NmUtMzg5Ny00YzFkLWI4YWQtYzMwMTA2MTQ0ZjE3-aCmbMEJizuL70Xu5"

def summarize(source_text):
    client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a high school chemistry teacher. Respond with a summary of the text that is both accurate and easy to understand in the user message.",
            },
            {
                "role": "user",
                "content": source_text,
            }
        ],
        model=MODEL_NAME,
        stream=False,
    )
    return chat_completion.choices[0].message.content

def qgen(source_text):
    client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a high school chemistry teacher. Respond with a list of 20 questions that can be answered by the text in the user message. If the text discusses a theory, there must be a question about it. You must have at least one question about each of the chemical elements or compounds mentioned in the text. The text in the user message must contain specific answers to each question. Each question must be on its own line. Just list the questions without any introductory text or numbers.",
            },
            {
                "role": "user",
                "content": source_text,
            }
        ],
        model=MODEL_NAME,
        stream=False,
    )
    return chat_completion.choices[0].message.content

def agen(source_text, question):
    client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a high school chemistry teacher. Answer the student question strictly based on the context below.\n" + source_text,
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model=MODEL_NAME,
        stream=False,
    )
    return chat_completion.choices[0].message.content

def main():
    results = [];
    arguments = sys.argv[1:]

    with open(arguments[0], 'r', newline='') as txtfile:
        txt_data = txtfile.read()
        paras = re.split('^\s*$', txt_data, flags=re.MULTILINE) 

        current_line = 0
        for p in paras:
            current_line = current_line + 1
            print(str(current_line) + ' of ' + str(len(paras)))
            print(p + "\n\n\n")
            if len(p.strip()) == 0:
                continue

            result = []
            result.append(p)
            result.append(summarize(p))
            results.append(result)

            qs = qgen(p)
            for q in qs.splitlines():
                if len(q.strip()) == 0 or (not q.endswith("?")):
                    continue
                print('question: ' + q)
                result = []
                result.append(p)
                result.append(q + "\n" + agen(p, q))
                results.append(result)

    with open(arguments[1], 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in results:
            writer.writerow(row)

if __name__ == "__main__":
    main()
