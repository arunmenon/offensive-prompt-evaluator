import json
import re
import os
import argparse

# Load exceptions from JSON file
def load_exceptions(exceptions_file):
    try:
        with open(exceptions_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The exceptions file '{exceptions_file}' was not found.")
        return {}

# Load the prompt template from a text file
def load_prompt_template(prompt_file):
    try:
        with open(prompt_file, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The prompt template file '{prompt_file}' was not found.")
        return None

# Extract placeholders (e.g., {placeholder}) from the prompt template
def extract_placeholders(prompt_template):
    return re.findall(r"\{(.*?)\}", prompt_template)

# Function to dynamically replace placeholders in the prompt template
def generate_dynamic_prompt(prompt_template, exceptions):
    placeholders = extract_placeholders(prompt_template)
    
    for placeholder in placeholders:
        if placeholder in exceptions:
            prompt_template = prompt_template.replace(f"{{{placeholder}}}", ", ".join(exceptions[placeholder]))
        else:
            raise ValueError(f"Error: Placeholder '{placeholder}' not found in exceptions config. Unable to generate prompt.")
    
    return prompt_template

# Function to find the next available prompt number
def get_next_prompt_number(destination_folder):
    # List all files in the destination folder
    files = os.listdir(destination_folder)
    
    # Find all files that follow the naming convention 'PromptX.txt' (X is a number)
    prompt_files = [f for f in files if f.startswith("Prompt") and f.endswith(".txt")]
    
    # Extract the numbers from the file names and find the highest one
    numbers = []
    for file in prompt_files:
        try:
            number = int(re.search(r'Prompt(\d+)\.txt', file).group(1))
            numbers.append(number)
        except (AttributeError, ValueError):
            continue  # Skip files that don't match the pattern
    
    if numbers:
        return max(numbers) + 1  # Return the next available number
    else:
        return 1  # Start from 1 if no prompt files are found

# Function to save the generated prompt to a file
def save_prompt_to_file(prompt, destination_folder):
    # Find the next available prompt number
    next_number = get_next_prompt_number(destination_folder)
    
    # Construct the file name (e.g., 'Prompt1.txt', 'Prompt2.txt', etc.)
    file_name = f"Prompt{next_number}.txt"
    file_path = os.path.join(destination_folder, file_name)
    
    # Save the prompt to the file
    with open(file_path, 'w') as file:
        file.write(prompt)
    
    print(f"Generated prompt saved as: {file_path}")

# Main function to handle command-line arguments
def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Generate a dynamic prompt based on exceptions and a prompt template.")
    parser.add_argument('--exceptions', type=str, required=True, help='Path to the exceptions config file (JSON).')
    parser.add_argument('--template', type=str, required=True, help='Path to the prompt template file (TXT).')
    parser.add_argument('--destination', type=str, required=True, help='Folder to save the generated prompt.')

    # Parse the arguments
    args = parser.parse_args()

    # Load exceptions from JSON
    exceptions = load_exceptions(args.exceptions)

    # Load the prompt template from the text file
    prompt_template = load_prompt_template(args.template)

    if prompt_template:
        try:
            # Generate the dynamic prompt with the loaded exceptions
            dynamic_prompt = generate_dynamic_prompt(prompt_template, exceptions)
            
            # Save the generated prompt to the destination folder
            save_prompt_to_file(dynamic_prompt, args.destination)

        except ValueError as e:
            print(str(e))  # Print the error and exit

if __name__ == "__main__":
    main()
