import argparse
import subprocess
import google.generativeai as genai
import os
from dotenv import load_dotenv
import shutil
from enum import Enum, auto
from typing import List, Dict, Optional
import re

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
        # Split commands by newlines and run each one
        commands = [cmd.strip() for cmd in command.split('\n') if cmd.strip()]
        for cmd in commands:
            # For git commands, we need to handle them specially
            if cmd.startswith('git'):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(result.stdout)
                else:
                    print(f"Error: {result.stderr}")
                    return False
            # For copy commands
            elif cmd.startswith('xcopy') or cmd.startswith('copy'):
                current_dir = os.getcwd()
                cmd = cmd.replace('source_folder_path', current_dir)
                if 'destination_folder_path' in cmd:
                    parent_dir = os.path.dirname(current_dir)
                    cmd = cmd.replace('destination_folder_path', parent_dir)
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(result.stdout)
                else:
                    print(f"Error: {result.stderr}")
                    return False
            # For other commands
            else:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(result.stdout)
                else:
                    print(f"Error: {result.stderr}")
                    return False
        return True
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return False

def handle_command(args):
    # Check if the command is for code analysis
    if args.command.startswith('analyze:'):
        code = args.command[8:].strip()  # Remove 'analyze:' prefix
        result = analyze_code(code)
        
        print("\n=== Lexical Analysis Results ===")
        if result['success']:
            print("Tokens found:")
            for token in result['tokens']:
                print(f"  {token}")
        else:
            print(f"Error during lexical analysis: {result['error']}")
        
        print("\n=== Semantic Analysis Results ===")
        if result['semantic_errors']:
            print("Semantic errors found:")
            for error in result['semantic_errors']:
                print(f"  {error}")
        else:
            print("No semantic errors found.")
        
        print("\n=== Symbol Table ===")
        for var_name, info in result['symbol_table'].items():
            print(f"  {var_name}: {info['type']} (declared at line {info['line']})")
        
        return
    
    # Add context about the current directory and environment
    context = f"""Current directory: {os.getcwd()}
    Operating System: Windows
    Task: {args.command}
    Please provide a Windows command that will work in the current directory."""
    
    response = model.generate_content(
        f"""You are a bot that gives back specific cmd commands required to complete the task mentioned. 
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
