# GEHU Command Line Interface

A powerful command-line interface tool that uses Google's Gemini AI to generate and execute commands based on natural language input.

## Features

- Natural language command generation
- Direct command execution
- File creation and manipulation
- Git operations
- Code analysis capabilities
- Support for multiple programming languages

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gehu
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Usage

### Basic Commands

1. Generate a command without executing:
```bash
gehu "your command description"
```

2. Generate and execute a command:
```bash
gehu "your command description" --run
```

### Examples

1. Create a Python file:
```bash
gehu "create a file test.py with a hello world function" --run
```

2. Create a C++ file:
```bash
gehu "create a file binary.cpp with binary search code" --run
```

3. Git operations:
```bash
gehu "initialize git repository and make first commit" --run
```

4. Code Analysis:
```bash
gehu "analyze: def hello(): print('Hello')"
```

### Code Analysis Features

The tool includes a built-in code analyzer that can:
- Perform lexical analysis
- Perform semantic analysis
- Generate symbol tables
- Detect common programming errors

Example:
```bash
gehu "analyze: var x = 10; const y = 20; x = y;"
```

## Supported Operations

1. File Operations:
   - Create new files
   - Write content to files
   - Append content to files
   - Support for multiple programming languages

2. Git Operations:
   - Initialize repositories
   - Add files
   - Commit changes
   - Push to remote

3. Code Analysis:
   - Lexical analysis
   - Semantic analysis
   - Symbol table generation
   - Error detection

## Requirements

- Python 3.7+
- Google API key for Gemini AI
- Required Python packages (see requirements.txt)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
