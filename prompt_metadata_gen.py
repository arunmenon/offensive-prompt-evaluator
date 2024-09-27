import argparse
import datetime
import json
import os
import time
import openai
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


import requests

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cosine similarity threshold for determining whether fields are the "Same as before"
SIMILARITY_THRESHOLD = 0.9

# Predefined Content Categories
PREDEFINED_CATEGORIES = {
    "nudity": "Nudity and Sexually Suggestive Content",
    "sexual content": "Nudity and Sexually Suggestive Content",
    "violence": "Violence and Dangerous Activities",
    "dangerous activities": "Violence and Dangerous Activities",
    "hate speech": "Hate Speech, Symbols, and Discriminatory Content",
    "discriminatory content": "Hate Speech, Symbols, and Discriminatory Content",
    "culturally insensitive": "Culturally or Religiously Insensitive Content",
    "illegal products": "Illegal or Unsafe Products",
    "misleading information": "Misleading or Harmful Information",
    "graphic imagery": "Graphic and Violent Imagery",
    # Add other mappings as needed
}


# Function to get the next version number for a given prompt file
def get_next_version(existing_metadata, prompt_file_location):
    if prompt_file_location in existing_metadata['Prompt File Location'].values:
        existing_versions = existing_metadata[existing_metadata['Prompt File Location'] == prompt_file_location]['Version']
        return existing_versions.max() + 1
    return 1


# Function to load existing metadata if available
def load_existing_metadata(metadata_file):
    if os.path.exists(metadata_file):
        print(f"Loading existing metadata from {metadata_file}")
        df = pd.read_csv(metadata_file)
        if 'Prompt File Location' not in df.columns:
            print("'Prompt File Location' column not found in existing metadata file, initializing new DataFrame.")
            return pd.DataFrame(columns=['Prompt File Location', 'Version', 'Prompt Title', 'Creation Date', 'Last Modified Date', 'Summary', 'Content Categories', 'Prompt Scope', 'Risk Sensitivity', 'Prompt Score', 'Score Reason'])
        return df
    else:
        print("No existing metadata found, creating new file.")
        return pd.DataFrame(columns=['Prompt File Location', 'Version', 'Prompt Title', 'Creation Date', 'Last Modified Date', 'Summary', 'Content Categories', 'Prompt Scope', 'Risk Sensitivity', 'Prompt Score', 'Score Reason'])

# Function to extract file metadata
def extract_file_metadata(file_path):
    stats = os.stat(file_path)
    creation_time = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    modified_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    return creation_time, modified_time

# Function to ensure data types are correctly processed
def sanitize_field_value(value):
    """Helper function to ensure field values are correctly processed."""
    if isinstance(value, (int, float)):  # If the value is numeric, return it as is for numeric fields
        print(f"Numeric field detected: {value}")
        return value
    elif isinstance(value, str):  # If the value is a string, lower it
        print(f"String field detected: {value}")
        return value.lower()
    print(f"Converting field value to string: {value}")
    return str(value)  # Convert any other type to a string

# Function to calculate cosine similarity between two pieces of text
def cosine_sim(text1, text2):
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0][1]  # Return the similarity between the two texts



def evaluate_metadata_changes(existing_metadata, prompt_file_location, new_metadata, similarity_threshold=SIMILARITY_THRESHOLD):
    # Fetch the last 5 entries for the given prompt file
    previous_versions = existing_metadata[existing_metadata['Prompt File Location'] == prompt_file_location].tail(5)
    
    # If no prior data exists, no need for comparison
    if previous_versions.empty:
        print(f"No previous versions found for {prompt_file_location}. Proceeding with new metadata.")
        return new_metadata
    
    updated_metadata = {}

    for field in ['Summary', 'Content Categories', 'Prompt Scope', 'Risk Sensitivity', 'Prompt Score', 'Score Reason']:
        last_value = previous_versions[field].values[-1] if not previous_versions[field].empty else ""
        new_value = sanitize_field_value(new_metadata[field])

        # Skip comparison for numeric fields like "Prompt Score"
        if field == "Prompt Score":
            if last_value != new_value:
                print(f"New value detected for {field}. Updating to: {new_value}")
                updated_metadata[field] = new_value
            else:
                print(f"No changes in {field}. Keeping 'Same as before'.")
                updated_metadata[field] = "Same as before"
            continue

        # Calculate cosine similarity between old and new values for text fields
        if isinstance(last_value, str) and isinstance(new_value, str):
            similarity = cosine_sim(last_value, new_value)
            print(f"Comparing {field}. Cosine similarity: {similarity}")
        else:
            similarity = 0

        if similarity >= similarity_threshold:
            print(f"{field} marked as 'Same as before' due to high similarity.")
            updated_metadata[field] = "Same as before"
        elif similarity >= 0.7:  # Minor differences
            print(f"{field} marked as 'Slightly updated'.")
            updated_metadata[field] = f"Slightly updated: {new_value}"
        else:
            print(f"{field} updated with new value: {new_value}")
            updated_metadata[field] = new_value

    # Keep the title unchanged if it exists
    if not previous_versions['Prompt Title'].empty:
        updated_metadata['Prompt Title'] = previous_versions.iloc[-1]['Prompt Title']
        print(f"Keeping title unchanged: {updated_metadata['Prompt Title']}")
    else:
        updated_metadata['Prompt Title'] = new_metadata['Prompt Title']
        print(f"Setting new title: {updated_metadata['Prompt Title']}")

    return updated_metadata


# Function to map categories returned by GPT-4 to predefined ones with fuzzy matching
# Simplified category mapping
def map_categories_to_predefined(gpt_categories):
    mapped_categories = [PREDEFINED_CATEGORIES.get(cat.lower().strip(), None) for cat in gpt_categories]
    mapped_categories = list(filter(None, mapped_categories))  # Remove None values
    if not mapped_categories:
        print(f"No categories mapped for GPT categories: {gpt_categories}")
    return mapped_categories


# Maximum retries and backoff parameters
MAX_RETRIES = 5
BACKOFF_FACTOR = 2

def generate_metadata_from_prompt(prompt_text):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Make GPT-4 API call to generate metadata
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates metadata for prompt evaluation. Always respond in valid JSON format."},
                    {"role": "user", "content": f"Generate the following metadata for this prompt: \n\nPrompt: {prompt_text}\n\nReturn the result in this structured JSON format exactly:\n{{\"title\": \"Prompt Title\", \"summary\": \"Short summary (20-30 words)\", \"categories\": [\"List of content categories like nudity, violence, etc.\"], \"scope\": \"Broad or specific\", \"risk_sensitivity\": \"Low, Medium, or High\", \"prompt_score\": \"1 to 5 (5 being very clear and safe, 1 being unclear or risky)\", \"score_reason\": \"Why this score was given\"}}"}
                ],
                max_tokens=300,
                n=1,
                temperature=0.5,
                timeout=30  # Timeout in 30 seconds if no response
            )

            # Process the GPT-4 response
            metadata = response['choices'][0]['message']['content'].strip()

            # Validate JSON format
            if metadata.startswith('{') and metadata.endswith('}'):
                metadata_dict = json.loads(metadata)
            else:
                print("GPT-4 response is not a valid JSON object.")
                print(f"Raw response: {metadata}")
                return None

            # Map categories to predefined categories
            gpt_categories = metadata_dict.get('categories', [])
            mapped_categories = map_categories_to_predefined(gpt_categories)
            print(f"GPT-4 Categories: {gpt_categories}")
            #print(f"Mapped Predefined Categories: {mapped_categories}")

            metadata_dict['categories'] = gpt_categories
            return metadata_dict

        except requests.exceptions.Timeout:
            retries += 1
            print(f"Request timed out. Retrying {retries}/{MAX_RETRIES}...")
            time.sleep(BACKOFF_FACTOR ** retries)  # Exponential backoff

        except openai.error.RateLimitError:
            retries += 1
            wait_time = BACKOFF_FACTOR ** retries
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

        except openai.error.OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return None

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    print("Max retries exceeded. Failed to generate metadata.")
    return None

# Function to scan prompt files and generate metadata
def generate_prompt_metadata(prompts_folder, metadata_file="prompt_metadata.csv"):
    prompt_metadata = []

    # Load existing metadata if it exists
    existing_metadata = load_existing_metadata(metadata_file)
    
    # Check if prompts folder exists
    if not os.path.exists(prompts_folder):
        print(f"Error: The folder '{prompts_folder}' does not exist.")
        return

    print(f"Scanning folder {prompts_folder} for prompt files.")
    
    # Scan the folder for prompt files
    prompt_files = [f for f in os.listdir(prompts_folder) if f.endswith(".txt")]

    if not prompt_files:
        print(f"No prompt files found in the folder {prompts_folder}")
        return

    for prompt_file in prompt_files:
        prompt_path = os.path.join(prompts_folder, prompt_file)
        
        # Extract file metadata (creation date, modification date)
        creation_time, modified_time = extract_file_metadata(prompt_path)
        
        # Read the content of the prompt file
        with open(prompt_path, "r") as file:
            prompt_text = file.read()

        # Make a single GPT-4 call to generate all metadata
        print(f"Generating metadata for prompt file: {prompt_file}")
        metadata_dict = generate_metadata_from_prompt(prompt_text)  # Already returns a dict

        if metadata_dict is None:
            print(f"Skipping metadata generation for {prompt_file} due to GPT-4 error.")
            continue

        # Check if the prompt already exists, and assign the correct version number
        version = get_next_version(existing_metadata, prompt_path)

        # Compare against the last 5 versions to evaluate changes
        final_metadata = evaluate_metadata_changes(existing_metadata, prompt_path, {
            'Prompt Title': metadata_dict.get('title', 'Untitled'),
            'Summary': metadata_dict.get('summary', 'No summary'),
            'Content Categories': ', '.join(metadata_dict.get('categories', [])),
            'Prompt Scope': metadata_dict.get('scope', 'Unknown'),
            'Risk Sensitivity': metadata_dict.get('risk_sensitivity', 'Unknown'),
            'Prompt Score': metadata_dict.get('prompt_score', 'Unknown'),
            'Score Reason': metadata_dict.get('score_reason', 'Unknown')
        })

        # Add metadata to the list
        prompt_metadata.append({
            'Prompt File Location': prompt_path,
            'Version': version,
            'Prompt Title': final_metadata['Prompt Title'],
            'Creation Date': creation_time,
            'Last Modified Date': modified_time,
            'Summary': final_metadata['Summary'],
            'Content Categories': final_metadata['Content Categories'],
            'Prompt Scope': final_metadata['Prompt Scope'],
            'Risk Sensitivity': final_metadata['Risk Sensitivity'],
            'Prompt Score': final_metadata['Prompt Score'],
            'Score Reason': final_metadata['Score Reason']
        })

        print(f"Metadata for {prompt_file} (version {version}) generated successfully.")

        # Pause to avoid rate-limiting from OpenAI API
        time.sleep(1)  # Adjust based on your API limits

    # Convert the new metadata into a DataFrame
    new_metadata_df = pd.DataFrame(prompt_metadata)

    # Concatenate with the existing metadata and save the CSV
    final_metadata_df = pd.concat([existing_metadata, new_metadata_df], ignore_index=True)
    final_metadata_df.to_csv(metadata_file, index=False)
    print(f"Prompt metadata successfully updated in {metadata_file}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Generate metadata for prompt files.")
    parser.add_argument('--prompts_folder', type=str, required=True, help="The folder containing prompt files.")
    parser.add_argument('--output_file', type=str, default="prompt_metadata.csv", help="The output CSV file to store the metadata.")

    # Parse the arguments
    args = parser.parse_args()

    # Generate prompt metadata based on the provided folder and output file
    generate_prompt_metadata(prompts_folder=args.prompts_folder, metadata_file=args.output_file)

if __name__ == "__main__":
    main()
