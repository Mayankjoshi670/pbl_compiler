import json
import csv
import os
import datetime
from typing import List, Dict, Set
from collections import defaultdict
import difflib
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal output
init()

class CommandManager:
    def __init__(self):
        self.commands = [
            {"command": "cd", "category": "Navigation", "description": "Change the current directory.", 
             "os": ["Windows", "Linux", "Unix"], "example": "cd C:\\Users"},
            {"command": "dir", "category": "Navigation", "description": "List files and directories in the current directory.",
             "os": ["Windows"], "example": "dir /p"},
            {"command": "ls", "category": "Navigation", "description": "List directory contents (Linux/Unix/PowerShell).",
             "os": ["Linux", "Unix", "PowerShell"], "example": "ls -la"},
            {"command": "mkdir", "category": "File Management", "description": "Create a new directory.",
             "os": ["Windows", "Linux", "Unix"], "example": "mkdir new_folder"},
            {"command": "rmdir", "category": "File Management", "description": "Remove a directory.",
             "os": ["Windows", "Linux", "Unix"], "example": "rmdir /s /q old_folder"},
            {"command": "tree", "category": "Navigation", "description": "Display directory structure graphically.",
             "os": ["Windows"], "example": "tree /f"},
            {"command": "copy", "category": "File Management", "description": "Copy files and directories.",
             "os": ["Windows"], "example": "copy source.txt destination.txt"},
            {"command": "del", "category": "File Management", "description": "Delete files.",
             "os": ["Windows"], "example": "del /f file.txt"},
            {"command": "rm", "category": "File Management", "description": "Remove files or directories (Linux/Unix/PowerShell).",
             "os": ["Linux", "Unix", "PowerShell"], "example": "rm -rf directory/"},
            {"command": "ren", "category": "File Management", "description": "Rename files.",
             "os": ["Windows"], "example": "ren old.txt new.txt"},
            {"command": "type", "category": "File Management", "description": "Display contents of a text file.",
             "os": ["Windows"], "example": "type file.txt"},
            {"command": "move", "category": "File Management", "description": "Move files and directories.",
             "os": ["Windows"], "example": "move file.txt C:\\destination\\"},
            {"command": "systeminfo", "category": "System Information", "description": "Display system information.",
             "os": ["Windows"], "example": "systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\""},
            {"command": "ver", "category": "System Information", "description": "Display OS version.",
             "os": ["Windows"], "example": "ver"},
            {"command": "tasklist", "category": "System Information", "description": "Show running processes.",
             "os": ["Windows"], "example": "tasklist /v"},
            {"command": "ipconfig", "category": "Network", "description": "Display IP and network configuration.",
             "os": ["Windows"], "example": "ipconfig /all"},
            {"command": "ifconfig", "category": "Network", "description": "Display network configuration (Linux/Unix).",
             "os": ["Linux", "Unix"], "example": "ifconfig eth0"},
            {"command": "ping", "category": "Network", "description": "Test network connectivity.",
             "os": ["Windows", "Linux", "Unix"], "example": "ping google.com"},
            {"command": "netstat", "category": "Network", "description": "Show network connections and routing tables.",
             "os": ["Windows", "Linux", "Unix"], "example": "netstat -an"},
            {"command": "chkdsk", "category": "System Information", "description": "Check and repair disk errors.",
             "os": ["Windows"], "example": "chkdsk C: /f"},
            {"command": "help", "category": "Other", "description": "Display help information for commands."},
            {"command": "cls", "category": "Other", "description": "Clear the screen."},
            {"command": "exit", "category": "Other", "description": "Exit the command prompt."},
            {"command": "taskkill", "category": "System Information", "description": "Terminate a running process."},
            {"command": "robocopy", "category": "File Management", "description": "Robust file and directory copy utility."},
            {"command": "diskpart", "category": "System Information", "description": "Manage disks, partitions, and volumes."},
            {"command": "notepad", "category": "Other", "description": "Open Notepad for text editing."},
            {"command": "powershell", "category": "Other", "description": "Start a PowerShell session."},
            {"command": "echo", "category": "Other", "description": "Display a message or turn command echoing on/off."},
            {"command": "shutdown", "category": "System Information", "description": "Shut down or restart the computer."},
            {"command": "whoami", "category": "System Information", "description": "Display the current user name."},
            {"command": "hostname", "category": "System Information", "description": "Display the computer name."},
            {"command": "date", "category": "System Information", "description": "Display or set the date."},
            {"command": "time", "category": "System Information", "description": "Display or set the system time."},
            {"command": "attrib", "category": "File Management", "description": "Display or change file attributes."},
            {"command": "find", "category": "Other", "description": "Search for a text string in a file."},
            {"command": "findstr", "category": "Other", "description": "Search for strings in files."},
            {"command": "fc", "category": "File Management", "description": "Compare two files and display differences."},
            {"command": "xcopy", "category": "File Management", "description": "Copy files and directory trees."},
            {"command": "sfc", "category": "System Information", "description": "System File Checker - scan and repair system files."},
            {"command": "gpupdate", "category": "System Information", "description": "Update Group Policy settings."},
            {"command": "net", "category": "Network", "description": "Manage network resources."},
            {"command": "netsh", "category": "Network", "description": "Network shell utility."},
            {"command": "arp", "category": "Network", "description": "Display or modify the ARP cache."},
            {"command": "route", "category": "Network", "description": "Display or modify the IP routing table."},
            {"command": "nslookup", "category": "Network", "description": "Query DNS servers."},
            {"command": "tracert", "category": "Network", "description": "Trace route to a remote host."},
            {"command": "curl", "category": "Network", "description": "Transfer data from or to a server."},
            {"command": "wget", "category": "Network", "description": "Download files from the web (Linux/Unix/PowerShell)."},
        ]
        self.command_history = []
        self.usage_stats = defaultdict(int)
        self.categories = set()
        self.tags = set()
        self.aliases = {}
        self.backup_dir = "command_backups"
        
        # Initialize categories and tags
        self._initialize_categories_and_tags()
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def _initialize_categories_and_tags(self):
        """Initialize categories and tags from existing commands."""
        for cmd in self.commands:
            self.categories.add(cmd['category'])
            if 'tags' in cmd:
                self.tags.update(cmd['tags'])

    def validate_command(self, command: Dict) -> List[str]:
        """Validate a command entry and return list of errors."""
        errors = []
        required_fields = ['command', 'category', 'description', 'os', 'example']
        
        for field in required_fields:
            if field not in command:
                errors.append(f"Missing required field: {field}")
        
        if 'command' in command and not command['command'].strip():
            errors.append("Command name cannot be empty")
        
        if 'category' in command and command['category'] not in self.categories:
            errors.append(f"Invalid category: {command['category']}")
        
        return errors

    def add_command(self, command: Dict) -> bool:
        """Add a new command with validation."""
        errors = self.validate_command(command)
        if errors:
            print(f"Validation errors: {', '.join(errors)}")
            return False
        
        self.commands.append(command)
        self.command_history.append({
            'action': 'add',
            'command': command['command'],
            'timestamp': datetime.datetime.now().isoformat()
        })
        print(f"Added command: {command['command']}")
        return True

    def remove_command(self, command_name: str) -> bool:
        """Remove a command and track history."""
        for i, cmd in enumerate(self.commands):
            if cmd['command'] == command_name:
                removed = self.commands.pop(i)
                self.command_history.append({
                    'action': 'remove',
                    'command': command_name,
                    'timestamp': datetime.datetime.now().isoformat()
                })
                print(f"Removed command: {command_name}")
                return True
        print(f"Command not found: {command_name}")
        return False

    def update_command(self, command_name: str, updates: Dict) -> bool:
        """Update a command with validation."""
        for i, cmd in enumerate(self.commands):
            if cmd['command'] == command_name:
                updated_cmd = cmd.copy()
                updated_cmd.update(updates)
                
                errors = self.validate_command(updated_cmd)
                if errors:
                    print(f"Validation errors: {', '.join(errors)}")
                    return False
                
                self.commands[i] = updated_cmd
                self.command_history.append({
                    'action': 'update',
                    'command': command_name,
                    'timestamp': datetime.datetime.now().isoformat()
                })
                print(f"Updated command: {command_name}")
                return True
        print(f"Command not found: {command_name}")
        return False

    def track_usage(self, command_name: str):
        """Track command usage statistics."""
        self.usage_stats[command_name] += 1

    def get_usage_stats(self) -> Dict:
        """Get command usage statistics."""
        return dict(self.usage_stats)

    def add_alias(self, command_name: str, alias: str):
        """Add an alias for a command."""
        if command_name in [cmd['command'] for cmd in self.commands]:
            self.aliases[alias] = command_name
            print(f"Added alias '{alias}' for command '{command_name}'")
        else:
            print(f"Command not found: {command_name}")

    def get_command_by_alias(self, alias: str) -> Dict:
        """Get command by its alias."""
        if alias in self.aliases:
            command_name = self.aliases[alias]
            return next((cmd for cmd in self.commands if cmd['command'] == command_name), None)
        return None


def add_tag(self, command_name: str, tag: str):
        """Add a tag to a command."""
        for cmd in self.commands:
            if cmd['command'] == command_name:
                if 'tags' not in cmd:
                    cmd['tags'] = set()
                cmd['tags'].add(tag)
                self.tags.add(tag)
                print(f"Added tag '{tag}' to command '{command_name}'")
                return
        print(f"Command not found: {command_name}")

    def search_by_tag(self, tag: str) -> List[Dict]:
        """Search commands by tag."""
        return [cmd for cmd in self.commands if 'tags' in cmd and tag in cmd['tags']]

    def compare_commands(self, command1: str, command2: str) -> Dict:
        """Compare two commands and show differences."""
        cmd1 = next((cmd for cmd in self.commands if cmd['command'] == command1), None)
        cmd2 = next((cmd for cmd in self.commands if cmd['command'] == command2), None)
        
        if not cmd1 or not cmd2:
            return {"error": "One or both commands not found"}
        
        differences = {}
        for key in set(cmd1.keys()) | set(cmd2.keys()):
            if cmd1.get(key) != cmd2.get(key):
                differences[key] = {
                    'command1': cmd1.get(key),
                    'command2': cmd2.get(key)
                }
        
        return differences

    def create_backup(self, backup_name: str = None):
        """Create a backup of the current command list."""
        if not backup_name:
            backup_name = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        with open(backup_path, 'w') as f:
            json.dump({
                'commands': self.commands,
                'aliases': self.aliases,
                'categories': list(self.categories),
                'tags': list(self.tags),
                'timestamp': datetime.datetime.now().isoformat()
            }, f, indent=4)
        print(f"Created backup: {backup_path}")

    def restore_backup(self, backup_name: str):
        """Restore from a backup file."""
        backup_path = os.path.join(self.backup_dir, backup_name)
        if not os.path.exists(backup_path):
            print(f"Backup not found: {backup_name}")
            return False
        
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        self.commands = backup_data['commands']
        self.aliases = backup_data['aliases']
        self.categories = set(backup_data['categories'])
        self.tags = set(backup_data['tags'])
        print(f"Restored from backup: {backup_name}")
        return True

    def display_commands(self, commands: List[Dict] = None) -> None:
        """Display commands with syntax highlighting."""
        if commands is None:
            commands = self.commands
        
        print(f"\n{Fore.CYAN}{'Command':<15} {'Category':<20} {'OS':<25} Description{Style.RESET_ALL}")
        print("-" * 100)
        for cmd in commands:
            os_str = ", ".join(cmd.get("os", ["All"]))
            print(f"{Fore.GREEN}{cmd['command']:<15}{Style.RESET_ALL} "
                  f"{Fore.YELLOW}{cmd['category']:<20}{Style.RESET_ALL} "
                  f"{Fore.BLUE}{os_str:<25}{Style.RESET_ALL} "
                  f"{cmd['description']}")

    def search_commands(self, query: str) -> List[Dict]:
        """Search commands by name, category, or description."""
        query = query.lower()
        return [cmd for cmd in self.commands if 
                query in cmd['command'].lower() or 
                query in cmd['category'].lower() or 
                query in cmd['description'].lower()]

    def filter_by_os(self, os_name: str) -> List[Dict]:
        """Filter commands by operating system."""
        return [cmd for cmd in self.commands if os_name in cmd.get("os", [])]

    def filter_by_category(self, category: str) -> List[Dict]:
        """Filter commands by category."""
        return [cmd for cmd in self.commands if cmd['category'].lower() == category.lower()]

    def export_to_json(self, filename: str) -> None:
        """Export commands to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.commands, f, indent=4)
        print(f"Commands exported to {filename}")

    def export_to_csv(self, filename: str) -> None:
        """Export commands to a CSV file."""
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['command', 'category', 'description', 'os', 'example'])
            writer.writeheader()
            writer.writerows(self.commands)
        print(f"Commands exported to {filename}")

    def save_commands(self, filename: str) -> None:
        """Save the current command list to a file."""
        with open(filename, 'w') as f:
            json.dump(self.commands, f, indent=4)
        print(f"Commands saved to {filename}")

    def load_commands(self, filename: str) -> None:
        """Load commands from a file."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.commands = json.load(f)
            print(f"Commands loaded from {filename}")
        else:
            print(f"File {filename} not found")

def display_menu():
    """Display the enhanced main menu."""
    print(f"\n{Fore.CYAN}=== Command Manager Menu ==={Style.RESET_ALL}")
    print("1. Display all commands")
    print("2. Search commands")
    print("3. Filter by OS")
    print("4. Filter by category")
    print("5. Filter by tag")
    print("6. Export to JSON")
    print("7. Export to CSV")
    print("8. Add new command")
    print("9. Remove command")
    print("10. Update command")
    print("11. Add command alias")
    print("12. Add command tag")
    print("13. Compare commands")
    print("14. View usage statistics")
    print("15. Create backup")
    print("16. Restore from backup")
    print("17. View command history")
    print("0. Exit")
    return input("Select an option: ")


def main():
    manager = CommandManager()
    
    while True:
        choice = display_menu()
        
        if choice == "1":
            manager.display_commands()
        
        elif choice == "2":
            query = input("Enter search term: ")
            results = manager.search_commands(query)
            manager.display_commands(results)
        
        elif choice == "3":
            os_name = input("Enter OS (Windows/Linux/Unix/PowerShell): ")
            results = manager.filter_by_os(os_name)
            manager.display_commands(results)
        
        elif choice == "4":
            category = input("Enter category: ")
            results = manager.filter_by_category(category)
            manager.display_commands(results)
        
        elif choice == "5":
            tag = input("Enter tag: ")
            results = manager.search_by_tag(tag)
            manager.display_commands(results)
        
        elif choice == "6":
            filename = input("Enter JSON filename: ")
            manager.export_to_json(filename)
        
        elif choice == "7":
            filename = input("Enter CSV filename: ")
            manager.export_to_csv(filename)
        
        elif choice == "8":
            command = {
                "command": input("Enter command name: "),
                "category": input("Enter category: "),
                "description": input("Enter description: "),
                "os": input("Enter OS (comma-separated): ").split(","),
                "example": input("Enter example usage: ")
            }
            manager.add_command(command)
        
        elif choice == "9":
            command_name = input("Enter command name to remove: ")
            manager.remove_command(command_name)
        
        elif choice == "10":
            command_name = input("Enter command name to update: ")
            updates = {
                "category": input("Enter new category (or press Enter to skip): "),
                "description": input("Enter new description (or press Enter to skip): "),
                "os": input("Enter new OS (comma-separated) (or press Enter to skip): ").split(","),
                "example": input("Enter new example (or press Enter to skip): ")
            }
            # Remove empty updates
            updates = {k: v for k, v in updates.items() if v}
            manager.update_command(command_name, updates)
        
        elif choice == "11":
            command_name = input("Enter command name: ")
            alias = input("Enter alias: ")
            manager.add_alias(command_name, alias)
        
        elif choice == "12":
            command_name = input("Enter command name: ")
            tag = input("Enter tag: ")
            manager.add_tag(command_name, tag)
        
        elif choice == "13":
            cmd1 = input("Enter first command name: ")
            cmd2 = input("Enter second command name: ")
            differences = manager.compare_commands(cmd1, cmd2)
            print("\nDifferences:")
            for key, values in differences.items():
                print(f"{key}:")
                print(f"  Command 1: {values['command1']}")
                print(f"  Command 2: {values['command2']}")
        
        elif choice == "14":
            stats = manager.get_usage_stats()
            print("\nUsage Statistics:")
            for cmd, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
                print(f"{cmd}: {count} times")
        
        elif choice == "15":
            backup_name = input("Enter backup name (or press Enter for auto-generated name): ")
            manager.create_backup(backup_name if backup_name else None)
        
        elif choice == "16":
            backup_name = input("Enter backup name to restore: ")
            manager.restore_backup(backup_name)
        
        elif choice == "17":
            print("\nCommand History:")
            for entry in manager.command_history:
                print(f"{entry['timestamp']}: {entry['action']} - {entry['command']}")
        
        elif choice == "0":
            print("Goodbye!")
            break
        
        else:
            print("Invalid option. Please try again.")
