import os
import openai
import base64
import requests
import json
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from datetime import datetime
from multiprocessing import Pool, cpu_count
import time
import requests
import random
from tqdm import tqdm


# Set your OpenAI API key (make sure you've set this in your environment variables)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Helper function to encode an image in base64 (done once for each image)
def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The image file at {image_path} was not found.")
        return None

# Helper function to load the prompt from a text file
def load_prompt(prompt_file):
    try:
        with open(prompt_file, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: The prompt file '{prompt_file}' was not found.")
        return None



def send_prompt_with_image(encoded_image, prompt, max_retries=3):
    if not encoded_image:
        return "DUMMY"  # Return a dummy value if the image can't be encoded

    # Headers for OpenAI API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    # Payload to send to OpenAI with the prompt and encoded image
    payload = {
        "model": "gpt-4o-mini",  
        "messages": [
            {"role": "system", "content": "You are an image classifier checking for offensive content."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": f"data:image/jpeg;base64,{encoded_image}"}
        ],
        "max_tokens": 500  # Adjust this based on your needs
    }

    retries = 0  # Keep track of how many retries have been made

    while retries < max_retries:
        try:
            # Send the request to OpenAI
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            
            # Check if the response is OK (status code 200)
            response.raise_for_status()
            
            # Parse the response JSON
            result = response.json()
            
            if 'choices' in result and result['choices']:
                print(f"Successfully processed the image with prompt: {prompt}")
                return result['choices'][0]['message']['content'].strip()
            else:
                print("Error: No valid response from GPT-4-o")
                return "DUMMY"
        
        except requests.exceptions.HTTPError as http_err:
            # If we hit the rate limit (429 Too Many Requests), retry
            if response.status_code == 429:
                retries += 1
                # Randomized exponential backoff: base wait time + a small random float
                wait_time = 2 ** retries + random.uniform(0, 1)  # Adds some randomness to avoid clumping
                print(f"Rate limit reached. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
                time.sleep(wait_time)  # Wait before retrying
            else:
                print(f"HTTP error occurred: {http_err}")
                return "DUMMY"
        except requests.exceptions.RequestException as e:
            print(f"Error: API request failed - {e}")
            return "DUMMY"
    
    print("Error: Max retries reached. Returning DUMMY.")
    return "DUMMY"

# Function to parse the GPT-4-o response
def parse_gpt_response(response):
    """
    Parse the GPT-4-o response, expecting it in the structured JSON format.
    """
    try:
        # Check if the response is enclosed in backticks and clean it
        if response.startswith("```json"):
            response = response.replace("```json", "").replace("```", "").strip()

        # Parse the JSON response
        parsed_response = json.loads(response)

        # Check if the 'offensive' field is present and return the correct label
        return "offensive" if parsed_response.get("offensive", False) else "not_offensive"

    except json.JSONDecodeError:
        print("Error: Response not in valid JSON format")
        return "DUMMY"

# Load dataset with image paths and ground truth labels
def load_image_dataset(csv_path):
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: The dataset file '{csv_path}' was not found.")
        return pd.DataFrame()

# Pre-encode all images to avoid redundant encoding in every process
def encode_images(df):
    encoded_images = {}
    for image_path in df['image_path'].unique():
        encoded_images[image_path] = encode_image(image_path)
    return encoded_images

# Function to evaluate a single prompt
def evaluate_single_prompt(args):
    df, prompt_file, encoded_images = args
    prompt = load_prompt(prompt_file)
    if not prompt:
        return None  # Skip if the prompt couldn't be loaded

    predictions = []
    for _, row in df.iterrows():
        image_path = row['image_path']
        encoded_image = encoded_images.get(image_path)
        
        # Send image and prompt to GPT-4-o
        gpt_response = send_prompt_with_image(encoded_image, prompt)
        prediction = parse_gpt_response(gpt_response)
        
        predictions.append(prediction)

    return prompt_file, predictions

# Function to calculate precision, recall, and F1-score
def calculate_metrics(df, results):
    metrics = {}

    for prompt, predictions in results.items():
        ground_truth = df['label'].map(lambda x: 1 if x == 'offensive' else 0).tolist()
        predicted_labels = [1 if p == 'offensive' else 0 for p in predictions]

        precision = precision_score(ground_truth, predicted_labels, zero_division=0)
        recall = recall_score(ground_truth, predicted_labels, zero_division=0)
        f1 = f1_score(ground_truth, predicted_labels, zero_division=0)

        metrics[prompt] = {
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1
        }

    return metrics

# Function to save metrics to a file
def save_metrics(metrics, result_path):
    os.makedirs(result_path, exist_ok=True)
    for prompt, metric in metrics.items():
        metric_file = os.path.join(result_path, f"metrics_{os.path.basename(prompt)}.txt")
        with open(metric_file, 'w') as f:
            f.write(json.dumps(metric, indent=4))

# Main function to load dataset, run prompts in parallel, and calculate metrics


def main():
    # Path to the dataset and prompt files
    dataset_path = "./downloaded_images/Images_Ground_Truth.csv"  # Update this path
    prompts_folder = "prompts/"  # Folder containing multiple prompt text files

    # Load the dataset of images and labels
    df = load_image_dataset(dataset_path)
    if df.empty:
        return  # Exit if the dataset cannot be loaded

    # Pre-encode all images
    encoded_images = encode_images(df)

    # Get all prompt files from the folder
    prompts = [os.path.join(prompts_folder, f) for f in os.listdir(prompts_folder) if f.endswith(".txt")]

    # Set up multiprocessing pool to evaluate prompts in parallel
    num_processes = min(len(prompts), cpu_count())
    
    # Initialize tqdm progress bar with the total number of prompts
    with tqdm(total=len(prompts), desc="Evaluating Prompts", unit="prompt") as pbar:
        with Pool(num_processes) as pool:
            # For each completed prompt, update the progress bar manually
            results_list = []
            for result in pool.imap_unordered(evaluate_single_prompt, [(df, prompt, encoded_images) for prompt in prompts]):
                results_list.append(result)
                pbar.update(1)  # Update progress bar after each prompt evaluation

    # Process the results
    results = {prompt: predictions for prompt, predictions in results_list if predictions}

    # Calculate precision, recall, and F1-score
    metrics = calculate_metrics(df, results)

    # Print and analyze the metrics
    for prompt, metric in metrics.items():
        print(f"\nPrompt: {prompt}")
        print(f"Precision: {metric['Precision']}")
        print(f"Recall: {metric['Recall']}")
        print(f"F1-Score: {metric['F1-Score']}")
    
    # Save results for each prompt
    save_metrics(metrics, "results/")

if __name__ == "__main__":
    main()
