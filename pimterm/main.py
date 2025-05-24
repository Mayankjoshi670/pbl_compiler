import argparse
import subprocess
import google.generativeai as genai
import os
from dotenv import load_dotenv
import shutil

# Load environment variables from .env file
load_dotenv(encoding='utf-8')

# Configure Gemini API
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    try:
        with open('.env', 'r') as f:
            content = f.read().strip()
            if 'GOOGLE_API_KEY=' in content:
                api_key = content.split('GOOGLE_API_KEY=')[1].strip()
    except Exception:
        pass

if not api_key:
    print("Error: GOOGLE_API_KEY not found. Please set it in your .env file or environment variables.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def execute_command(command):
    try:
        # For git commands, we need to handle them specially
        if command.startswith('git'):
            # Split the command into parts
            parts = command.split()
            if parts[0] == 'git':
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(result.stdout)
                    return True
                else:
                    print(f"Error: {result.stderr}")
                    return False
        # For copy commands
        elif command.startswith('xcopy') or command.startswith('copy'):
            # Replace source_folder_path with actual current directory
            current_dir = os.getcwd()
            command = command.replace('source_folder_path', current_dir)
            # For copying to parent directory
            if 'destination_folder_path' in command:
                parent_dir = os.path.dirname(current_dir)
                command = command.replace('destination_folder_path', parent_dir)
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"Error: {result.stderr}")
                return False
        # For other commands
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"Error: {result.stderr}")
                return False
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return False

def handle_command(args):
    # Add context about the current directory and environment
    context = f"""Current directory: {os.getcwd()}
    Operating System: Windows
    Task: {args.command}
    Please provide a Windows command that will work in the current directory."""
    
    response = model.generate_content(
        f"""You are a bot that gives back specific Windows commands required to complete the task mentioned. 
        Please provide only the command itself, without any additional explanation. 
        If the solution requires multiple commands, provide them all in sequence.
        Make sure to use proper Windows command syntax.
        {context}"""
    )
    
    command = response.text.strip()
    print(f"Generated command: {command}")
    
    if args.run:
        print("\nExecuting command...")
        if execute_command(command):
            print("\nCommand executed successfully!")
        else:
            print("\nCommand execution failed!")

def handle_question(args):
    response = model.generate_content(
        f"""You will be asked questions that will be displayed in a cmd terminal.
        Make your answers short and in plain text. Don't add ethical warnings or redundant information.
        Answer in the language the question is asked.
        Question: {args.question}"""
    )
    print(response.text)

def main():
    parser = argparse.ArgumentParser(description="gehu Command Line Interface")
    parser.add_argument('command', type=str, help='Command or question to process')
    parser.add_argument('--run', '-r', action='store_true', help='Execute the generated command')
    
    args = parser.parse_args()
    handle_command(args)

if __name__ == "__main__":
    main()
