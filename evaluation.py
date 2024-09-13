import json
import re
import openai  # or another LLM API library
import os
from datetime import datetime
import time
from tqdm import tqdm

def load_dataset(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def query_llm(question):

    prompt = f""" TODO: add prompt here

Problem: {question}

Solution:"""
    
    r = response(prompt)

    return r

def extract_answer(llm_response):
    # Look for the last number mentioned in the response
    numbers = re.findall(r'\b\d+\b', llm_response)
    if numbers:
        last_number = int(numbers[-1])
        if 0 <= last_number <= 22:
            return last_number
    
    # If no valid number is found, return None
    return None

def response(prompt):

    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
            )
            break  # If the operation is successful, exit the loop
        except Exception as e:
            print(f"An error occurred: {e}. Retrying in 5 seconds...")
            time.sleep(10)  # Wait for 5 seconds before retrying
            attempt += 1
            if attempt == max_attempts:
                return Exception

    return completion.choices[0].message.content.strip()

def evaluate_response(llm_response, solution):
    llm_answer = extract_answer(llm_response)
    correct_answer = extract_answer(solution)
    
    if llm_answer is None or correct_answer is None:
        return "Error: Could not extract a valid answer"
    
    if llm_answer == correct_answer:
        return "Correct"
    else:
        return f"Incorrect (LLM: {llm_answer}, Correct: {correct_answer})"

def main(num_questions=None):
    dataset_folder = 'dataset'
    log_folder = 'evaluation_log'
    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(log_folder, f'evaluation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

    json_files = [f for f in os.listdir(dataset_folder) if f.endswith('.json')]
    
    if num_questions is not None:
        json_files = json_files[:num_questions]

    evaluation_results = []
    correct_count = 0
    total_count = 0

    # 使用tqdm创建进度条
    for filename in tqdm(json_files, desc="Evaluating", unit="question"):
        file_path = os.path.join(dataset_folder, filename)
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        question = data['question']
        solution = data['solution']

        llm_response = query_llm(question)
        evaluation_result = evaluate_response(llm_response, solution)
        
        result_entry = {
            "file": filename,
            "question": question,
            "correct_solution": solution,
            "llm_response": llm_response,
            "evaluation_result": evaluation_result
        }
        evaluation_results.append(result_entry)

        total_count += 1
        if evaluation_result == "Correct":
            correct_count += 1

        # 更新进度条描述以显示当前正确率
        current_accuracy = (correct_count / total_count) * 100
        tqdm.write(f"Current accuracy: {current_accuracy:.2f}% ({correct_count}/{total_count})")

    with open(log_file, 'w') as log:
        json.dump(evaluation_results, log, indent=2)

    final_accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    print(f"\nEvaluation completed. Final accuracy: {final_accuracy:.2f}% ({correct_count}/{total_count})")

if __name__ == "__main__":
    main(num_questions=20)  # Change this number to evaluate a different number of questions
