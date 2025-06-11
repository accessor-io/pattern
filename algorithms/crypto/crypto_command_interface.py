
from crypto_utils import CryptoCommandUtils
from typing import List, Dict, Set, Optional
import cmd
import readline
import sys
import termios
import tty
import os
from collections import defaultdict
import textwrap
import time
from crypto_operations import CryptoOperations
from datetime import datetime

# Enhanced ANSI Color codes and styling
class Style:
    # Basic colors
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_BLUE = '\033[44m'
    
    # Text styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'
    
    # Reset
    ENDC = '\033[0m'

    @staticmethod
    def cmd(text):
        """Format interface command"""
        return f"{Style.RED}{text}{Style.ENDC}"

    @staticmethod
    def op(text):
        """Format crypto operation"""
        return f"{Style.BLUE}{text}{Style.ENDC}"

    @staticmethod
    def category(text):
        """Format category header"""
        return f"{Style.YELLOW}{Style.BOLD}{text}{Style.ENDC}"

class CryptoCategories:
    """Categorization of crypto operations"""
    CATEGORIES = {
        'INITIALIZATION': {
            'description': 'Start and setup operations',
            'operations': {'INIT', 'BEGIN', 'START', 'LOAD'}
        },
        'SECURITY': {
            'description': 'Security and verification operations',
            'operations': {'SECURE', 'VERIFY', 'GUARD', 'ENCRYPT', 'DECRYPT'}
        },
        'PROCESSING': {
            'description': 'Data processing operations',
            'operations': {'PROCESS', 'EXECUTE', 'TRANSFER', 'SYNC'}
        },
        'MEMORY': {
            'description': 'Memory management operations',
            'operations': {'MEMORY', 'BUFFER', 'CACHE', 'STORE'}
        },
        'NETWORK': {
            'description': 'Network and communication operations',
            'operations': {'NETWORK', 'GATEWAY', 'ROUTE', 'FORWARD'}
        },
        'DATA': {
            'description': 'Data operations',
            'operations': {'DATA', 'QUERY', 'READ', 'WRITE'}
        },
        'ENS': {
            'description': 'Ethereum Name Service operations',
            'operations': {
                'RESOLVE', 'REGISTER', 'SET_ADDRESS', 'GET_OWNER', 'SET_RESOLVER',
                'CREATE_SUBDOMAIN', 'LIST_SUBDOMAINS', 'DELETE_SUBDOMAIN',
                'BATCH_CREATE', 'BATCH_DELETE', 'TRANSFER_SUBDOMAIN',
                'FILTER_SUBDOMAINS', 'EXPORT_SUBDOMAINS'
            }
        }
    }

    @staticmethod
    def get_category(operation: str) -> str:
        """Get the category of an operation"""
        for category, info in CryptoCategories.CATEGORIES.items():
            if operation in info['operations']:
                return category
        return 'MISC'

class CursorControl:
    CLEAR_SCREEN = '\033[2J'
    CLEAR_LINE = '\033[K'
    UP = '\033[A'
    DOWN = '\033[B'
    RIGHT = '\033[C'
    LEFT = '\033[D'
    HOME = '\033[H'

class CryptoCommandValidator:
    def __init__(self):
        self.utils = CryptoCommandUtils()
        self._build_operation_graph()

    def _build_operation_graph(self):
        """Build a graph of valid operation sequences"""
        self.operation_graph = defaultdict(set)
        self.all_operations = set()
        
        # Analyze all commands to build valid operation sequences
        for _, command in self.utils.commands:
            ops = command.split('_')
            self.all_operations.update(ops)
            
            # Build connections between consecutive operations
            for i in range(len(ops) - 1):
                self.operation_graph[ops[i]].add(ops[i + 1])

    def get_valid_next_operations(self, current_sequence: List[str]) -> Set[str]:
        """Get valid next operations based on the current sequence"""
        if not current_sequence:
            # If starting new sequence, return all operations that appear at start of commands
            return {cmd.split('_')[0] for _, cmd in self.utils.commands}
        
        last_op = current_sequence[-1]
        return self.operation_graph[last_op]

    def validate_sequence(self, sequence: List[str]) -> tuple[bool, str]:
        """Validate if a sequence of operations is valid"""
        if not sequence:
            return True, "Empty sequence is valid"
            
        # Check if each operation exists
        invalid_ops = [op for op in sequence if op not in self.all_operations]
        if invalid_ops:
            return False, f"Invalid operations: {', '.join(invalid_ops)}"
            
        # Check if sequence follows valid paths
        for i in range(len(sequence) - 1):
            if sequence[i + 1] not in self.operation_graph[sequence[i]]:
                return False, f"Invalid transition: {sequence[i]} -> {sequence[i + 1]}"
                
        return True, "Valid sequence"

    def find_example_commands(self, sequence: List[str], max_results: int = 3) -> List[str]:
        """Find example commands that contain the given sequence"""
        return self.utils.get_command_sequence(sequence)[:max_results]

class KeyCodes:
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    RIGHT = '\x1b[C'
    LEFT = '\x1b[D'
    ENTER = '\r'
    ESCAPE = '\x1b'
    CTRL_C = '\x03'

class ArrowKeyHandler:
    def __init__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
    
    def __enter__(self):
        tty.setraw(sys.stdin.fileno())
        return self
    
    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def get_key(self):
        """Get a single keypress"""
        char = sys.stdin.read(1)
        if char == '\x1b':
            char = sys.stdin.read(2)
            return '\x1b' + char
        return char

class CryptoCommandInterface(cmd.Cmd):
    intro = f"""
{Style.CYAN}╔════════════════════════════════════════════════════════════════╗
║             {Style.YELLOW}Crypto Command Interface v1.0{Style.CYAN}                   ║
║                                                                ║
║  {Style.category("Interface Commands:")}{Style.CYAN}                                        ║
║  {Style.cmd("start")}      : Start a new command sequence                   ║
║  {Style.cmd("add")} <op>   : Add operation to current sequence              ║
║  {Style.cmd("cycle")}      : Cycle through available operations             ║
║  {Style.cmd("category")}   : Cycle through operation categories             ║
║  {Style.cmd("validate")}   : Validate current sequence                      ║
║  {Style.cmd("show")}       : Show current sequence                          ║
║  {Style.cmd("clear")}      : Clear current sequence                         ║
║  {Style.cmd("toggle")}     : Toggle dynamic mode                            ║
║  {Style.cmd("help")}       : Show this help message                         ║
║  {Style.cmd("quit")}       : Exit the program                              ║
║                                                                ║
║  {Style.category("Operation Categories:")}{Style.CYAN}                                      ║
║  - Initialization (INIT, BEGIN, START, LOAD)                   ║
║  - Security (SECURE, VERIFY, GUARD, ENCRYPT)                  ║
║  - Processing (PROCESS, EXECUTE, TRANSFER)                    ║
║  - Memory (MEMORY, BUFFER, CACHE)                            ║
║  - Network (NETWORK, GATEWAY, ROUTE)                         ║
║  - Data (DATA, QUERY, READ, WRITE)                          ║
║  - ENS (RESOLVE, REGISTER, SET_ADDRESS, GET_OWNER,          ║
║        CREATE_SUBDOMAIN, LIST_SUBDOMAINS, DELETE_SUBDOMAIN) ║
╚════════════════════════════════════════════════════════════════╝{Style.ENDC}
    """
    prompt = f'{Style.GREEN}crypto>{Style.ENDC} '

    def __init__(self):
        super().__init__()
        self.validator = CryptoCommandValidator()
        self.current_sequence: List[str] = []
        self.dynamic_mode = True
        self.current_suggestions = []
        self.suggestion_index = 0
        self.category_index = 0
        self.current_category = list(CryptoCategories.CATEGORIES.keys())[0]
        self.terminal_height = os.get_terminal_size().lines
        self.terminal_width = os.get_terminal_size().columns
        self.output_file = "crypto_sequence_output.txt"
        self.crypto_ops = CryptoOperations()
        self.data_to_process = None
        
        # Initialize ENS with default provider (can be changed later)
        self.crypto_ops.initialize_ens("https://mainnet.infura.io/v3/YOUR-PROJECT-ID")

    def _update_display(self):
        """Update the dynamic display with current sequence and suggestions"""
        if not self.dynamic_mode:
            return

        # Clear screen and move cursor to top
        print(CursorControl.CLEAR_SCREEN + CursorControl.HOME, end='')
        
        # Show header - simple single line
        print(f"┌{'─' * 50}┐")
        print(f"│{Style.YELLOW}{'Crypto Command Builder':^50}{Style.ENDC}│")
        print(f"└{'─' * 50}┘")
        
        # Show current sequence - clean and simple
        print(f"Sequence: {Style.CYAN}", end='')
        if self.current_sequence:
            print(" → ".join(self.current_sequence))
        else:
            print(f"{Style.DIM}Start by selecting an operation{Style.ENDC}")
        print()
        
        # Simple controls line
        print(f"Controls: {Style.DIM}↑/↓: Select | Enter: Add | Esc: Cancel | Tab: Help{Style.ENDC}")
        print()
        
        # Category header - clean and minimal
        print(f"{Style.YELLOW}{self.current_category}{Style.ENDC}")
        print(f"{Style.DIM}{CryptoCategories.CATEGORIES[self.current_category]['description']}{Style.ENDC}")
        print(f"{'─' * 50}")
        
        # Display operations in current category as simple vertical list
        operations_by_category = defaultdict(list)
        valid_next = self.validator.get_valid_next_operations(self.current_sequence)
        self.current_suggestions = sorted(list(valid_next))
        
        for op in self.current_suggestions:
            cat = CryptoCategories.get_category(op)
            operations_by_category[cat].append(op)
        
        if operations_by_category[self.current_category]:
            ops = operations_by_category[self.current_category]
            visible_range = 8  # Show 8 operations at a time
            start_idx = max(0, self.suggestion_index - visible_range // 2)
            end_idx = min(len(ops), start_idx + visible_range)
            
            # Adjust start_idx if we're near the end
            if end_idx - start_idx < visible_range:
                start_idx = max(0, end_idx - visible_range)
            
            # Show scroll indicator if needed
            if start_idx > 0:
                print(f"{Style.DIM}▲ More{Style.ENDC}")
            
            # Display operations with minimal decoration
            for i, op in enumerate(ops[start_idx:end_idx]):
                if op == self.current_suggestions[self.suggestion_index]:
                    print(f"{Style.BLUE}▶ {op}{Style.ENDC}")
                else:
                    print(f"  {Style.CYAN}{op}{Style.ENDC}")
            
            # Show scroll indicator if needed
            if end_idx < len(ops):
                print(f"{Style.DIM}▼ More{Style.ENDC}")
            
            # Add some padding
            remaining_lines = visible_range - (end_idx - start_idx)
            for _ in range(remaining_lines):
                print()
        else:
            print(f"{Style.DIM}No operations available in this category{Style.ENDC}")
            for _ in range(8):  # Maintain consistent height
                print()
        
        # Simple tip at bottom
        print(f"{'─' * 50}")
        print(f"{Style.DIM}Tip: Operations are grouped by category for easy access{Style.ENDC}")
        print()
        print(f"Commands: {Style.DIM}execute - Run sequence | save - Save sequence{Style.ENDC}")
        print(f"{Style.GREEN}crypto>{Style.ENDC} ", end='', flush=True)

    def selection_mode(self):
        """Enter arrow key selection mode"""
        with ArrowKeyHandler() as handler:
            while True:
                self._update_display()
                
                key = handler.get_key()
                
                if key == KeyCodes.UP:
                    # Move up in current category
                    valid_ops = [op for op in self.current_suggestions 
                               if CryptoCategories.get_category(op) == self.current_category]
                    if valid_ops:
                        current_op = self.current_suggestions[self.suggestion_index]
                        try:
                            current_idx = valid_ops.index(current_op)
                            new_idx = (current_idx - 1) % len(valid_ops)
                            self.suggestion_index = self.current_suggestions.index(valid_ops[new_idx])
                        except ValueError:
                            self.suggestion_index = 0
                
                elif key == KeyCodes.DOWN:
                    # Move down in current category
                    valid_ops = [op for op in self.current_suggestions 
                               if CryptoCategories.get_category(op) == self.current_category]
                    if valid_ops:
                        current_op = self.current_suggestions[self.suggestion_index]
                        try:
                            current_idx = valid_ops.index(current_op)
                            new_idx = (current_idx + 1) % len(valid_ops)
                            self.suggestion_index = self.current_suggestions.index(valid_ops[new_idx])
                        except ValueError:
                            self.suggestion_index = 0
                
                elif key == KeyCodes.LEFT:
                    # Previous category
                    categories = list(CryptoCategories.CATEGORIES.keys())
                    self.category_index = (self.category_index - 1) % len(categories)
                    self.current_category = categories[self.category_index]
                    self.suggestion_index = 0
                
                elif key == KeyCodes.RIGHT:
                    # Next category
                    categories = list(CryptoCategories.CATEGORIES.keys())
                    self.category_index = (self.category_index + 1) % len(categories)
                    self.current_category = categories[self.category_index]
                    self.suggestion_index = 0
                
                elif key == KeyCodes.ENTER:
                    if self.current_suggestions:
                        selected = self.current_suggestions[self.suggestion_index]
                        self.current_sequence.append(selected)
                        return True
                
                elif key == KeyCodes.ESCAPE or key == KeyCodes.CTRL_C:
                    return False
                
                elif key == '\t':  # Tab key for help
                    self._show_help()

    def _show_help(self):
        """Show help overlay"""
        print(CursorControl.CLEAR_SCREEN)
        print(f"""
┌{'─' * 48}┐
│{Style.YELLOW}{'Quick Help':^48}{Style.ENDC}│
└{'─' * 48}┘

{Style.YELLOW}Navigation:{Style.ENDC}
• Up/Down: Move through operations
• Left/Right: Switch categories
• Enter: Add selected operation
• Esc: Cancel selection

{Style.YELLOW}Categories:{Style.ENDC}
• INITIALIZATION: Start and setup
• SECURITY: Protection and verification
• PROCESSING: Data handling
• MEMORY: Storage operations
• NETWORK: Communication
• DATA: Information management

{Style.YELLOW}Tips:{Style.ENDC}
• Operations are grouped by function
• Build sequences step by step
• Use Tab anytime to see this help

Press any key to continue...
        """)
        with ArrowKeyHandler() as handler:
            handler.get_key()  # Wait for any key

    def do_select(self, arg):
        """Enter arrow key selection mode"""
        self.selection_mode()

    def do_add(self, arg):
        """Add an operation to the current sequence"""
        if not arg:
            # If no argument, enter selection mode
            self.selection_mode()
        else:
            # Original add behavior
            operation = arg.upper()
            valid_next = self.validator.get_valid_next_operations(self.current_sequence)
            
            if operation not in valid_next:
                print(f"\n{Style.RED}Error: '{operation}' is not a valid next operation{Style.ENDC}")
                return
                
            self.current_sequence.append(operation)
            self.suggestion_index = 0
            
            if self.dynamic_mode:
                self._update_display()
            else:
                print(f"\n{Style.GREEN}Added: {Style.YELLOW}{operation}{Style.ENDC}")
                print(f"{Style.BLUE}Current sequence:{Style.ENDC}", 
                      f"{Style.YELLOW}{' -> '.join(self.current_sequence)}{Style.ENDC}")
                self.do_suggest("")

    def do_start(self, arg):
        """Start a new command sequence"""
        self.current_sequence = []
        self.suggestion_index = 0
        print(f"\n{Style.GREEN}Starting new sequence.{Style.ENDC}")
        if self.dynamic_mode:
            self._update_display()
        else:
            self.do_suggest("")

    def do_validate(self, arg):
        """Validate the current sequence"""
        if not self.current_sequence:
            print(f"\n{Style.YELLOW}No sequence to validate. Use 'start' to begin a new sequence.{Style.ENDC}")
            return
            
        is_valid, message = self.validator.validate_sequence(self.current_sequence)
        print(f"\n{Style.BLUE}Sequence: {Style.YELLOW}{' -> '.join(self.current_sequence)}{Style.ENDC}")
        status_color = Style.GREEN if is_valid else Style.RED
        print(f"{Style.BLUE}Status: {status_color}{'Valid' if is_valid else 'Invalid'}{Style.ENDC}")
        print(f"{Style.BLUE}Message: {status_color}{message}{Style.ENDC}")

    def do_suggest(self, arg):
        """Get suggestions for next valid operations"""
        valid_next = self.validator.get_valid_next_operations(self.current_sequence)
        if not valid_next:
            print(f"\n{Style.YELLOW}No valid next operations available.{Style.ENDC}")
            return
            
        print(f"\n{Style.GREEN}Valid next operations:{Style.ENDC}")
        self._print_suggestions(valid_next)

    def _print_suggestions(self, suggestions: Set[str]):
        """Helper method to print suggestions in a formatted way"""
        # Sort and group suggestions for better readability
        sorted_suggestions = sorted(suggestions)
        for i, suggestion in enumerate(sorted_suggestions):
            if i % 4 == 0:
                print()
            print(f"{Style.YELLOW}{suggestion:20}{Style.ENDC}", end="")
        print("\n")

    def do_examples(self, arg):
        """Show example commands that contain the current sequence"""
        if not self.current_sequence:
            print(f"\n{Style.YELLOW}No sequence specified. Use 'start' to begin a new sequence.{Style.ENDC}")
            return
            
        examples = self.validator.find_example_commands(self.current_sequence)
        if not examples:
            print(f"\n{Style.YELLOW}No example commands found for the current sequence.{Style.ENDC}")
            return
            
        print(f"\n{Style.BLUE}Example commands containing sequence {Style.YELLOW}{' -> '.join(self.current_sequence)}{Style.ENDC}:")
        for i, example in enumerate(examples, 1):
            print(f"{Style.GREEN}{i}. {Style.CYAN}{example}{Style.ENDC}")

    def do_show(self, arg):
        """Show the current sequence"""
        if not self.current_sequence:
            print(f"\n{Style.YELLOW}No current sequence. Use 'start' to begin a new sequence.{Style.ENDC}")
            return
            
        print(f"\n{Style.BLUE}Current sequence: {Style.YELLOW}{' -> '.join(self.current_sequence)}{Style.ENDC}")

    def do_clear(self, arg):
        """Clear the current sequence"""
        self.current_sequence = []
        print(f"\n{Style.GREEN}Sequence cleared.{Style.ENDC}")

    def do_quit(self, arg):
        """Exit the program"""
        print(f"\n{Style.GREEN}Goodbye!{Style.ENDC}")
        return True

    def default(self, line):
        """Handle unknown commands"""
        print(f"\n{Style.RED}Unknown command: {line}{Style.ENDC}")
        print(f"{Style.YELLOW}Type 'help' for a list of commands.{Style.ENDC}")

    def emptyline(self):
        """Do nothing on empty line"""
        pass

    def execute_sequence(self):
        """Execute the current sequence with real crypto operations"""
        if not self.current_sequence:
            print(f"{Style.RED}No sequence to execute. Build a sequence first.{Style.ENDC}")
            return

        print(f"\n{Style.GREEN}Executing crypto sequence...{Style.ENDC}")
        
        try:
            for step, operation in enumerate(self.current_sequence, 1):
                print(f"\n{Style.YELLOW}Step {step}: {operation}{Style.ENDC}")
                
                if operation.startswith('INIT'):
                    result = self.crypto_ops.initialize_system()
                    print(f"Initialized crypto system: {result['message']}")
                    print(f"Public key saved to: {result['public_key_path']}")
                
                elif operation.startswith('SECURE'):
                    if not self.data_to_process:
                        self.data_to_process = input(f"{Style.CYAN}Enter data to encrypt: {Style.ENDC}")
                    result = self.crypto_ops.secure_data(self.data_to_process)
                    print(f"Data encrypted: {result['message']}")
                    print(f"Saved to: {result['file']}")
                
                elif operation.startswith('VERIFY'):
                    result = self.crypto_ops.verify_data()
                    if result['valid']:
                        print(f"{Style.GREEN}✓ Data verified successfully{Style.ENDC}")
                    else:
                        print(f"{Style.RED}✗ Data verification failed{Style.ENDC}")
                
                elif operation.startswith('PROCESS'):
                    result = self.crypto_ops.process_data()
                    print(f"Data processed: {result['message']}")
                    print(f"Decrypted data saved to: {result['file']}")
                    print(f"Content: {result['decrypted_data']}")
                
                time.sleep(0.5)  # Brief pause between operations
            
            print(f"\n{Style.GREEN}Sequence executed successfully!{Style.ENDC}")
            
            # Show operation log
            print(f"\n{Style.YELLOW}Operation Log:{Style.ENDC}")
            for entry in self.crypto_ops.get_operation_log():
                timestamp = entry['timestamp'].split('T')[1][:8]  # Extract time
                status = entry['details']['status']
                status_color = Style.GREEN if status == 'success' else Style.RED
                print(f"{Style.DIM}{timestamp}{Style.ENDC} - "
                      f"{entry['operation']}: {status_color}{status}{Style.ENDC}")
        
        except Exception as e:
            print(f"\n{Style.RED}Error executing sequence: {str(e)}{Style.ENDC}")

    def do_execute(self, arg):
        """Execute the current sequence"""
        self.execute_sequence()

    def do_save(self, arg):
        """Save the current sequence to a file"""
        if not self.current_sequence:
            print(f"{Style.RED}No sequence to save. Build a sequence first.{Style.ENDC}")
            return
            
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"sequence_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write(" -> ".join(self.current_sequence))
            
        print(f"{Style.GREEN}Sequence saved to: {filename}{Style.ENDC}")

    def do_data(self, arg):
        """Set data to be processed"""
        self.data_to_process = arg
        print(f"{Style.GREEN}Data set for processing: {arg}{Style.ENDC}")

    async def do_ens(self, arg: str) -> None:
        """Handle ENS operations"""
        args = arg.split()
        if not args:
            print(f"{Style.RED}Error: ENS operation required{Style.ENDC}")
            self.print_ens_help()
            return

        operation = args[0].upper()
        if operation not in CryptoCategories.CATEGORIES['ENS']['operations']:
            print(f"{Style.RED}Error: Invalid ENS operation{Style.ENDC}")
            self.print_ens_help()
            return

        try:
            if operation == "RESOLVE":
                if len(args) != 2:
                    print(f"{Style.RED}Error: Usage: ens resolve <name>{Style.ENDC}")
                    return
                result = await self.crypto_ops.resolve_ens_name(args[1])
                
            elif operation == "REGISTER":
                if len(args) < 2:
                    print(f"{Style.RED}Error: Usage: ens register <name> [duration_years]{Style.ENDC}")
                    return
                duration = int(args[2]) if len(args) > 2 else 1
                result = await self.crypto_ops.register_ens_name(args[1], duration)
                
            elif operation == "SET_ADDRESS":
                if len(args) != 3:
                    print(f"{Style.RED}Error: Usage: ens set_address <name> <address>{Style.ENDC}")
                    return
                result = await self.crypto_ops.set_ens_address(args[1], args[2])
                
            elif operation == "GET_OWNER":
                if len(args) != 2:
                    print(f"{Style.RED}Error: Usage: ens get_owner <name>{Style.ENDC}")
                    return
                result = await self.crypto_ops.get_ens_owner(args[1])
                
            elif operation == "SET_RESOLVER":
                if len(args) != 3:
                    print(f"{Style.RED}Error: Usage: ens set_resolver <name> <resolver_address>{Style.ENDC}")
                    return
                result = await self.crypto_ops.set_ens_resolver(args[1], args[2])
                
            elif operation == "CREATE_SUBDOMAIN":
                if len(args) < 3:
                    print(f"{Style.RED}Error: Usage: ens create_subdomain <domain> <subdomain> [owner_address]{Style.ENDC}")
                    return
                owner = args[3] if len(args) > 3 else None
                result = await self.crypto_ops.create_subdomain(args[1], args[2], owner)
                
            elif operation == "LIST_SUBDOMAINS":
                if len(args) != 2:
                    print(f"{Style.RED}Error: Usage: ens list_subdomains <domain>{Style.ENDC}")
                    return
                result = await self.crypto_ops.list_subdomains(args[1])
                
            elif operation == "DELETE_SUBDOMAIN":
                if len(args) != 3:
                    print(f"{Style.RED}Error: Usage: ens delete_subdomain <domain> <subdomain>{Style.ENDC}")
                    return
                result = await self.crypto_ops.delete_subdomain(args[1], args[2])
                
            elif operation == "BATCH_CREATE":
                if len(args) < 4 or len(args) % 2 != 0:
                    print(f"{Style.RED}Error: Usage: ens batch_create <domain> <subdomain1> [owner1] <subdomain2> [owner2] ...{Style.ENDC}")
                    return
                    
                domain = args[1]
                subdomains = []
                for i in range(2, len(args), 2):
                    subdomain_info = {
                        "name": args[i],
                        "owner": args[i + 1] if i + 1 < len(args) else None
                    }
                    subdomains.append(subdomain_info)
                    
                result = await self.crypto_ops.batch_create_subdomains(domain, subdomains)
                
            elif operation == "FILTER_SUBDOMAINS":
                if len(args) < 3:
                    print(f"{Style.RED}Error: Usage: ens filter_subdomains <domain> <filter_type> <value> ...{Style.ENDC}")
                    print("Filter types: name_contains, owner, has_address, created_after, resolver_type")
                    return
                    
                domain = args[1]
                filters = {}
                for i in range(2, len(args), 2):
                    if i + 1 >= len(args):
                        break
                    filter_type = args[i]
                    filter_value = args[i + 1]
                    
                    if filter_type == "has_address":
                        filter_value = filter_value.lower() == "true"
                    elif filter_type == "created_after":
                        filter_value = datetime.fromisoformat(filter_value)
                        
                    filters[filter_type] = filter_value
                    
                result = await self.crypto_ops.filter_subdomains(domain, filters)
                
            elif operation == "TRANSFER_SUBDOMAIN":
                if len(args) != 4:
                    print(f"{Style.RED}Error: Usage: ens transfer_subdomain <domain> <subdomain> <new_owner>{Style.ENDC}")
                    return
                result = await self.crypto_ops.transfer_subdomain(args[1], args[2], args[3])
                
            elif operation == "EXPORT_SUBDOMAINS":
                if len(args) < 2:
                    print(f"{Style.RED}Error: Usage: ens export_subdomains <domain> [format]{Style.ENDC}")
                    print("Supported formats: json, csv, yaml (default: json)")
                    return
                format = args[2] if len(args) > 2 else "json"
                result = await self.crypto_ops.export_subdomains(args[1], format)

            # Display result
            if result["status"] == "success":
                print(f"{Style.GREEN}Success:{Style.ENDC}")
                if operation == "LIST_SUBDOMAINS" or operation == "FILTER_SUBDOMAINS":
                    subdomains = result.get("subdomains") or result.get("filtered_subdomains", [])
                    print(f"\n{Style.CYAN}Subdomains for {result['domain']}:{Style.ENDC}")
                    for subdomain in subdomains:
                        print(f"\n{Style.YELLOW}Subdomain:{Style.ENDC}")
                        for key, value in subdomain.items():
                            print(f"  {Style.CYAN}{key}:{Style.ENDC} {value}")
                    if operation == "FILTER_SUBDOMAINS":
                        print(f"\n{Style.CYAN}Filter Summary:{Style.ENDC}")
                        print(f"  Total subdomains: {result['total_count']}")
                        print(f"  Filtered subdomains: {result['filtered_count']}")
                        print(f"  Applied filters: {result['filters_applied']}")
                else:
                    for key, value in result.items():
                        if key != "status":
                            print(f"  {Style.CYAN}{key}:{Style.ENDC} {value}")
            else:
                print(f"{Style.RED}Error: {result['message']}{Style.ENDC}")

        except Exception as e:
            print(f"{Style.RED}Error: {str(e)}{Style.ENDC}")

    def print_ens_help(self):
        """Print ENS command help"""
        print(f"\n{Style.YELLOW}ENS Operations:{Style.ENDC}")
        print(f"""
{Style.CYAN}Basic Operations:{Style.ENDC}
  resolve <name>                    : Resolve ENS name to address
  register <name> [duration_years]  : Register new ENS name
  set_address <name> <address>      : Set address for ENS name
  get_owner <name>                  : Get owner of ENS name
  set_resolver <name> <resolver>    : Set resolver for ENS name

{Style.CYAN}Subdomain Operations:{Style.ENDC}
  create_subdomain <domain> <subdomain> [owner]  : Create new subdomain
  list_subdomains <domain>                       : List all subdomains
  delete_subdomain <domain> <subdomain>          : Delete subdomain
  transfer_subdomain <domain> <sub> <new_owner>  : Transfer subdomain ownership

{Style.CYAN}Batch Operations:{Style.ENDC}
  batch_create <domain> <sub1> [owner1] <sub2> [owner2] ...  : Create multiple subdomains

{Style.CYAN}Advanced Operations:{Style.ENDC}
  filter_subdomains <domain> <filter_type> <value> ...  : Filter subdomains
  export_subdomains <domain> [format]                   : Export subdomain data

{Style.CYAN}Filter Types:{Style.ENDC}
  - name_contains   : Filter by name
  - owner          : Filter by owner address
  - has_address    : Filter by address presence (true/false)
  - created_after  : Filter by creation date (ISO format)
  - resolver_type  : Filter by resolver type (public/custom)

{Style.CYAN}Export Formats:{Style.ENDC}
  - json (default)
  - csv
  - yaml
""")

    def do_set_provider(self, arg: str) -> None:
        """Set the Ethereum provider URL"""
        if not arg:
            print(f"{Style.RED}Error: Provider URL required{Style.ENDC}")
            return
            
        result = self.crypto_ops.initialize_ens(arg)
        if result["status"] == "success":
            print(f"{Style.GREEN}Successfully connected to network: {result['network']}{Style.ENDC}")
        else:
            print(f"{Style.RED}Error: {result['message']}{Style.ENDC}")

    def do_set_private_key(self, arg: str) -> None:
        """Set the private key for ENS operations"""
        if not arg:
            print(f"{Style.RED}Error: Private key required{Style.ENDC}")
            return
            
        result = self.crypto_ops.initialize_ens(
            self.crypto_ops.w3.provider.endpoint_uri if self.crypto_ops.w3 else "https://mainnet.infura.io/v3/YOUR-PROJECT-ID",
            arg
        )
        
        if result["status"] == "success":
            print(f"{Style.GREEN}Successfully set private key{Style.ENDC}")
        else:
            print(f"{Style.RED}Error: {result['message']}{Style.ENDC}")

def main():
    try:
        interface = CryptoCommandInterface()
        interface.cmdloop()
    except KeyboardInterrupt:
        print(f"\n{Style.GREEN}Goodbye!{Style.ENDC}")
        sys.exit(0)

if __name__ == "__main__":
    main() 