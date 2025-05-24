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

# Compiler Components

class TokenType(Enum):

  # Keywords

  IF = auto()

  ELSE = auto()

  WHILE = auto()

  FOR = auto()

  FUNCTION = auto()

  RETURN = auto()

  VAR = auto()

  CONST = auto()

  # Identifiers and literals

  IDENTIFIER = auto()

  NUMBER = auto()

  STRING = auto()

  # Operators

  PLUS = auto()

  MINUS = auto()

  MULTIPLY = auto()

  DIVIDE = auto()

  ASSIGN = auto()

  EQUALS = auto()

  NOT_EQUALS = auto()

  # Delimiters

  LPAREN = auto() # (

  RPAREN = auto() # )

  LBRACE = auto() # {

  RBRACE = auto() # }

  SEMICOLON = auto()

  COMMA = auto()

  # Special

  EOF = auto()

class Token:

  def __init__(self, type: TokenType, value: str, line: int, column: int):

    self.type = type

    self.value = value

    self.line = line

    self.column = column

  def __str__(self):

    return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class Lexer:

  def __init__(self, source: str):

    self.source = source

    self.position = 0

    self.line = 1

    self.column = 1

    self.current_char = self.source[0] if source else None

    # Keywords mapping

    self.keywords = {

      'if': TokenType.IF,

      'else': TokenType.ELSE,

      'while': TokenType.WHILE,

      'for': TokenType.FOR,

      'function': TokenType.FUNCTION,

      'return': TokenType.RETURN,

      'var': TokenType.VAR,

      'const': TokenType.CONST

    }

  def advance(self):

    self.position += 1

    self.column += 1

    if self.position >= len(self.source):

      self.current_char = None

    else:

      self.current_char = self.source[self.position]

      if self.current_char == '\n':

        self.line += 1

        self.column = 0

  def skip_whitespace(self):

    while self.current_char and self.current_char.isspace():

      self.advance()

  def skip_comment(self):

    while self.current_char and self.current_char != '\n':

      self.advance()

  def identifier(self) -> Token:

    result = ''

    start_column = self.column

    while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):

      result += self.current_char

      self.advance()

    token_type = self.keywords.get(result, TokenType.IDENTIFIER)

    return Token(token_type, result, self.line, start_column)

  def number(self) -> Token:

    result = ''

    start_column = self.column

    while self.current_char and self.current_char.isdigit():

      result += self.current_char

      self.advance()

    return Token(TokenType.NUMBER, result, self.line, start_column)

  def string(self) -> Token:

    result = ''

    start_column = self.column

    self.advance() # Skip opening quote

    while self.current_char and self.current_char != '"':

      result += self.current_char

      self.advance()

    self.advance() # Skip closing quote

    return Token(TokenType.STRING, result, self.line, start_column)

  def get_next_token(self) -> Token:

    while self.current_char:

      if self.current_char.isspace():

        self.skip_whitespace()

        continue

      if self.current_char == '#':

        self.skip_comment()

        continue

      if self.current_char.isalpha() or self.current_char == '_':

        return self.identifier()

      if self.current_char.isdigit():

        return self.number()

      if self.current_char == '"':

        return self.string()

      # Handle operators and delimiters

      if self.current_char == '+':

        self.advance()

        return Token(TokenType.PLUS, '+', self.line, self.column - 1)

      if self.current_char == '-':

        self.advance()

        return Token(TokenType.MINUS, '-', self.line, self.column - 1)

      if self.current_char == '*':

        self.advance()

        return Token(TokenType.MULTIPLY, '*', self.line, self.column - 1)

      if self.current_char == '/':

        self.advance()

        return Token(TokenType.DIVIDE, '/', self.line, self.column - 1)

      if self.current_char == '=':

        self.advance()

        if self.current_char == '=':

          self.advance()

          return Token(TokenType.EQUALS, '==', self.line, self.column - 2)

        return Token(TokenType.ASSIGN, '=', self.line, self.column - 1)

      if self.current_char == '!':

        self.advance()

        if self.current_char == '=':

          self.advance()

          return Token(TokenType.NOT_EQUALS, '!=', self.line, self.column - 2)

      if self.current_char == '(':

        self.advance()

        return Token(TokenType.LPAREN, '(', self.line, self.column - 1)

      if self.current_char == ')':

        self.advance()

        return Token(TokenType.RPAREN, ')', self.line, self.column - 1)

      if self.current_char == '{':

        self.advance()

        return Token(TokenType.LBRACE, '{', self.line, self.column - 1)

      if self.current_char == '}':

        self.advance()

        return Token(TokenType.RBRACE, '}', self.line, self.column - 1)

      if self.current_char == ';':

        self.advance()

        return Token(TokenType.SEMICOLON, ';', self.line, self.column - 1)

      if self.current_char == ',':

        self.advance()

        return Token(TokenType.COMMA, ',', self.line, self.column - 1)

      raise Exception(f"Invalid character '{self.current_char}' at line {self.line}, column {self.column}")

    return Token(TokenType.EOF, '', self.line, self.column)

  def tokenize(self) -> List[Token]:

    tokens = []

    while True:

      token = self.get_next_token()

      tokens.append(token)

      if token.type == TokenType.EOF:

        break

    return tokens

class SemanticAnalyzer:

  def __init__(self):

    self.symbol_table = {} # Store variable declarations

    self.errors = []

  def analyze(self, tokens: List[Token]):

    self.errors = []

    self.symbol_table = {}

    i = 0

    while i < len(tokens):

      token = tokens[i]

      # Check for variable declarations

      if token.type in (TokenType.VAR, TokenType.CONST):

        if i + 2 >= len(tokens):

          self.errors.append(f"Invalid variable declaration at line {token.line}")

          break

        # Check for identifier

        if tokens[i + 1].type != TokenType.IDENTIFIER:

          self.errors.append(f"Expected identifier after {token.value} at line {token.line}")

          break

        var_name = tokens[i + 1].value

        # Check for assignment operator

        if tokens[i + 2].type != TokenType.ASSIGN:

          self.errors.append(f"Expected '=' after variable name at line {token.line}")

          break

        # Check if variable is already declared

        if var_name in self.symbol_table:

          self.errors.append(f"Variable '{var_name}' already declared at line {token.line}")

        else:

          self.symbol_table[var_name] = {

            'type': 'const' if token.type == TokenType.CONST else 'var',

            'line': token.line

          }

        i += 3

      else:

        i += 1

    return self.errors

def analyze_code(code: str) -> Dict:

  # Lexical Analysis

  lexer = Lexer(code)

  try:

    tokens = lexer.tokenize()

  except Exception as e:

    return {

      'success': False,

      'error': str(e),

      'tokens': [],

      'semantic_errors': []

    }

  # Semantic Analysis

  analyzer = SemanticAnalyzer()

  semantic_errors = analyzer.analyze(tokens)

  return {

    'success': len(semantic_errors) == 0,

    'tokens': tokens,

    'semantic_errors': semantic_errors,

    'symbol_table': analyzer.symbol_table

  }

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

  # Check if the command is for code analysis

  if args.command.startswith('analyze:'):

    code = args.command[8:].strip() # Remove 'analyze:' prefix

    result = analyze_code(code)

    print("\n=== Lexical Analysis Results ===")

    if result['success']:

      print("Tokens found:")

      for token in result['tokens']:

        print(f" {token}")

    else:

      print(f"Error during lexical analysis: {result['error']}")

    print("\n=== Semantic Analysis Results ===")

    if result['semantic_errors']:

      print("Semantic errors found:")

      for error in result['semantic_errors']:

        print(f" {error}")

    else:

      print("No semantic errors found.")

    print("\n=== Symbol Table ===")

    for var_name, info in result['symbol_table'].items():

      print(f" {var_name}: {info['type']} (declared at line {info['line']})")

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
