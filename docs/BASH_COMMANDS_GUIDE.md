# Bash Commands Guide - Learning from UV Disk Manager Project

This guide explains the important bash commands used during the development of UV Disk Manager. Each command is explained with examples from the actual project.

## Table of Contents

1. [Navigation Commands](#navigation-commands)
2. [File and Directory Operations](#file-and-directory-operations)
3. [File Inspection Commands](#file-inspection-commands)
4. [Search and Filter Commands](#search-and-filter-commands)
5. [Text Processing](#text-processing)
6. [System Information](#system-information)
7. [Redirection and Pipes](#redirection-and-pipes)
8. [Conditional Execution](#conditional-execution)
9. [Command Substitution](#command-substitution)
10. [Practical Examples from the Project](#practical-examples-from-the-project)

---

## Navigation Commands

### `cd` - Change Directory

**What it does**: Changes your current working directory.

**Examples from project**:
```bash
cd /home/amite/code/python                    # Go to python directory
cd ~/code/python/uv-disk-manager              # Go to project directory (using ~ for home)
cd ..                                          # Go up one directory
cd /tmp                                        # Go to temporary directory
```

**Key points**:
- `~` is a shortcut for your home directory (`/home/amite` in this case)
- `..` means parent directory
- `.` means current directory
- Absolute paths start with `/`, relative paths don't

---

## File and Directory Operations

### `mkdir -p` - Create Directories

**What it does**: Creates directories. The `-p` flag creates parent directories if needed and doesn't error if directory already exists.

**Examples from project**:
```bash
mkdir -p uv-disk-manager/core                  # Create core directory
mkdir -p uv-disk-manager/cli                   # Create cli directory
mkdir -p docs                                  # Create docs directory
```

**Why `-p` is useful**: Without `-p`, you'd need to create parent directories first. With `-p`, it creates the entire path at once.

### `ls` - List Files

**What it does**: Lists files and directories.

**Common variations**:
```bash
ls                                              # Basic listing
ls -la                                          # Long format, show all (including hidden)
ls -1                                           # One file per line
ls -lh                                          # Human-readable sizes
ls *.py                                         # List only .py files
ls -d */                                        # List only directories
```

**Examples from project**:
```bash
ls -la uv-disk-manager/*.py                    # List all Python files with details
ls -1 *.py *.txt *.md                          # List files, one per line
```

**Key flags**:
- `-l`: Long format (detailed info)
- `-a`: All files (including hidden ones starting with `.`)
- `-h`: Human-readable file sizes
- `-1`: One file per line
- `-d`: List directories themselves, not their contents

### `chmod +x` - Make Executable

**What it does**: Makes a file executable (allows it to be run as a program).

**Examples from project**:
```bash
chmod +x main.py                                # Make main.py executable
chmod +x install.sh                             # Make install.sh executable
chmod +x uv-disk-manager/main.py                # Make script executable
```

**Why it's needed**: Scripts need execute permission to be run directly. Without it, you'd need to run `python3 script.py` instead of `./script.py`.

### `rm -rf` - Remove Files/Directories

**What it does**: Removes files and directories. **Use with caution!**

**Flags**:
- `-r`: Recursive (delete directories and their contents)
- `-f`: Force (don't prompt for confirmation)

**Examples from project**:
```bash
rm -rf .venv                                    # Remove virtual environment
rm -rf /path/to/unused/project/.venv           # Remove specific venv
```

**⚠️ Warning**: `rm -rf` is powerful and permanent. Always double-check the path!

### `find` - Find Files

**What it does**: Searches for files and directories matching criteria.

**Common patterns**:
```bash
find . -name "*.py"                            # Find all .py files in current directory
find . -type f                                  # Find all files (not directories)
find . -type d                                  # Find all directories
find . -name ".venv"                            # Find .venv directories
find . -maxdepth 2 -name "*.py"                # Find .py files up to 2 levels deep
```

**Examples from project**:
```bash
find /home/amite/code/python -name ".venv"     # Find all .venv directories
find . -type f -name "*.py" -not -path "./.venv/*"  # Find .py files excluding .venv
find . -name "*.py" -exec wc -l {} +           # Count lines in all .py files
```

**Key options**:
- `.` means current directory (can use any path)
- `-name`: Match filename pattern
- `-type f`: Files only
- `-type d`: Directories only
- `-maxdepth N`: Limit search depth
- `-not -path`: Exclude paths
- `-exec`: Execute command on found files

---

## File Inspection Commands

### `cat` - Display File Contents

**What it does**: Prints the entire contents of a file to the terminal.

**Examples from project**:
```bash
cat pyproject.toml                              # Show pyproject.toml contents
cat README.md                                   # Show README
cat ~/.uv_space_log.json                        # Show log file
```

**Related commands**:
- `head -n 20 file.txt`: Show first 20 lines
- `tail -n 20 file.txt`: Show last 20 lines
- `less file.txt`: Interactive viewer (press `q` to quit)

### `wc -l` - Count Lines

**What it does**: Counts lines in a file or input.

**Examples from project**:
```bash
wc -l main.py                                   # Count lines in main.py
find . -name "*.py" -exec wc -l {} +           # Count lines in all .py files
cat file.txt | wc -l                           # Count lines via pipe
```

**Other `wc` options**:
- `wc -w`: Count words
- `wc -c`: Count characters
- `wc -l`: Count lines (most common)

### `du` - Disk Usage

**What it does**: Shows disk space used by files and directories.

**Common variations**:
```bash
du -sh directory/                               # Human-readable size summary
du -sb directory/                               # Size in bytes (for scripts)
du -h                                           # Human-readable, all subdirectories
```

**Examples from project**:
```bash
du -sh ~/.cache/uv                              # Check UV cache size
du -sh /home/amite/code/python/*/.venv          # Check all venv sizes
du -sb .venv                                    # Get exact size in bytes
```

**Key flags**:
- `-s`: Summary (total only, not per-file)
- `-h`: Human-readable (KB, MB, GB)
- `-b`: Bytes (exact size for calculations)

---

## Search and Filter Commands

### `grep` - Search Text

**What it does**: Searches for text patterns in files or input.

**Common patterns**:
```bash
grep "pattern" file.txt                         # Search for "pattern" in file
grep -r "pattern" .                             # Recursive search in all files
grep -i "pattern" file.txt                      # Case-insensitive search
grep -v "pattern" file.txt                      # Invert match (show non-matching)
```

**Examples from project**:
```bash
grep -v "No such file"                          # Filter out "No such file" errors
grep "import" *.py                              # Find all import statements
```

**Key flags**:
- `-r`: Recursive (search in subdirectories)
- `-i`: Case-insensitive
- `-v`: Invert match
- `-n`: Show line numbers

### `which` - Find Command Location

**What it does**: Shows the full path of a command.

**Examples from project**:
```bash
which uv                                        # Find where 'uv' command is located
which python3                                   # Find Python 3 location
which uv-disk-clean                             # Check if tool is installed
```

**Why it's useful**: Helps verify if a command is installed and accessible in your PATH.

### `test` - Test Conditions

**What it does**: Tests conditions (file existence, comparisons, etc.). Often used with `if` statements.

**Common tests**:
```bash
test -f file.txt                                # Test if file exists
test -d directory/                               # Test if directory exists
test -x script.sh                                # Test if file is executable
[ -f file.txt ]                                  # Same as test (bracket syntax)
```

**Examples from project**:
```bash
test -f requirements.txt && echo "File exists" || echo "File removed"
[ -d .venv ] && echo "Virtual env exists"
```

**Common test operators**:
- `-f`: File exists and is a regular file
- `-d`: Directory exists
- `-x`: File is executable
- `-r`: File is readable
- `-w`: File is writable

---

## Text Processing

### `head` and `tail` - View Parts of Files

**What it does**: Shows the beginning or end of a file or input.

**Examples from project**:
```bash
head -20 file.txt                               # First 20 lines
tail -10 file.txt                               # Last 10 lines
head -n 5                                        # First 5 lines from input
```

**Common use cases**:
- Preview large files
- Check recent log entries
- See file headers

### `sort` - Sort Lines

**What it does**: Sorts lines of text.

**Examples from project**:
```bash
ls -1 | sort                                    # Sort file listing
du -sh * | sort -h                              # Sort by human-readable size
find . -name "*.py" | sort                      # Sort found files
```

**Key flags**:
- `-h`: Human-readable numeric sort (for sizes like 1GB, 500MB)
- `-r`: Reverse sort
- `-n`: Numeric sort

---

## System Information

### `pwd` - Print Working Directory

**What it does**: Shows your current directory path.

**Example**:
```bash
pwd                                             # Output: /home/amite/code/python
```

### `echo` - Print Text

**What it does**: Prints text to the terminal.

**Examples from project**:
```bash
echo "Installation complete!"                   # Simple message
echo "✓ File removed"                           # With checkmark
echo $HOME                                       # Print variable value
```

**Special characters**:
- `\n`: New line
- `\t`: Tab
- `$VAR`: Variable expansion

---

## Redirection and Pipes

### `>` - Redirect Output to File

**What it does**: Saves command output to a file (overwrites existing file).

**Examples from project**:
```bash
python3 diagnose_disk_usage.py > report.txt     # Save output to file
echo "test" > output.txt                        # Write text to file
```

### `>>` - Append to File

**What it does**: Appends output to a file (doesn't overwrite).

**Example**:
```bash
echo "New line" >> report.txt                   # Add to end of file
```

### `|` - Pipe Operator

**What it does**: Sends output of one command as input to another.

**Examples from project**:
```bash
ls -1 *.py | wc -l                              # Count Python files
find . -name "*.py" | head -5                   # Find .py files, show first 5
du -sh * | sort -h                              # Show sizes, sort them
cat file.txt | grep "pattern"                   # Search in file contents
```

**Why it's powerful**: Chains commands together to create complex operations.

### `2>&1` - Redirect stderr to stdout

**What it does**: Combines error output with standard output.

**Examples from project**:
```bash
ls *.txt 2>&1 | grep -v "No such file"         # Hide "file not found" errors
command 2>&1 | head -10                         # Show both output and errors
```

**Understanding**:
- `1` = stdout (standard output)
- `2` = stderr (error output)
- `2>&1` = redirect stderr to wherever stdout is going

---

## Conditional Execution

### `&&` - Logical AND

**What it does**: Runs second command only if first succeeds.

**Examples from project**:
```bash
test -f file.txt && echo "File exists"          # Only echo if file exists
mkdir -p dir && cd dir                          # Create dir, then enter it
uv sync && ./install.sh                         # Run install only if sync succeeds
```

**How it works**: If first command exits with code 0 (success), run second command.

### `||` - Logical OR

**What it does**: Runs second command only if first fails.

**Examples from project**:
```bash
test -f file.txt || echo "File not found"       # Echo if file doesn't exist
command || echo "Error occurred"                 # Show error message on failure
```

**How it works**: If first command exits with non-zero code (failure), run second command.

### Combining `&&` and `||`

**Example**:
```bash
test -f file.txt && echo "Exists" || echo "Missing"
```

This reads as: "If file exists, echo 'Exists', otherwise echo 'Missing'"

---

## Command Substitution

### `$()` - Command Substitution

**What it does**: Executes a command and uses its output as a value.

**Examples from project**:
```bash
echo "Report generated at: $(date)"             # Insert current date
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"    # Get script's directory
choice=$(Prompt.ask "Enter number")            # Capture user input
```

**Alternative syntax**: `` `command` `` (backticks, less preferred)

**Why it's useful**: Allows you to use command output as part of another command.

### Variables

**Common variables**:
```bash
$HOME                                           # Home directory path
$PATH                                           # Command search path
$PWD                                            # Current directory
$$                                              # Current process ID
$?                                              # Exit code of last command
```

**Examples from project**:
```bash
cd $HOME/code/python                            # Use home directory variable
export PATH="$HOME/.local/bin:$PATH"            # Add to PATH
```

---

## Practical Examples from the Project

### Example 1: Check if File Exists and Remove It

```bash
test -f requirements.txt && rm requirements.txt || echo "File already removed"
```

**What it does**:
1. Test if `requirements.txt` exists
2. If yes, remove it
3. If no, print message

### Example 2: Count Lines in Python Files

```bash
find . -name "*.py" -not -path "./.venv/*" -exec wc -l {} + | tail -1
```

**What it does**:
1. Find all `.py` files
2. Exclude `.venv` directory
3. Count lines in each file
4. Show total (last line)

### Example 3: List Files with Specific Extensions

```bash
ls -1 *.py *.txt *.md 2>&1 | grep -v "No such file" || echo "All cleaned up!"
```

**What it does**:
1. List files with extensions `.py`, `.txt`, `.md`
2. Hide "No such file" errors
3. If no files found, show success message

### Example 4: Check Installation

```bash
which uv-disk-clean && echo "✓ Installed" || echo "✗ Not found"
```

**What it does**:
1. Check if `uv-disk-clean` is in PATH
2. Show success or failure message

### Example 5: Get Directory Size

```bash
du -sh ~/.cache/uv                              # Human-readable size
du -sb ~/.cache/uv | cut -f1                    # Size in bytes (for scripts)
```

**What it does**:
1. Get directory size
2. Format as human-readable or bytes
3. `cut -f1` extracts first field (the size number)

### Example 6: Find and Process Files

```bash
find /home/amite/code/python -name ".venv" -exec du -sh {} \; | sort -h
```

**What it does**:
1. Find all `.venv` directories
2. Get size of each
3. Sort by size (human-readable)

**Breaking it down**:
- `find ... -name ".venv"`: Find directories named `.venv`
- `-exec du -sh {} \;`: Run `du -sh` on each found item
  - `{}` is replaced with each found path
  - `\;` ends the `-exec` command
- `| sort -h`: Sort the results

### Example 7: Safe File Operations

```bash
[ -f file.txt ] && cat file.txt || echo "File not found"
```

**What it does**:
1. Check if file exists (using bracket syntax)
2. If yes, display it
3. If no, show error message

---

## Tips and Best Practices

### 1. Always Quote Variables

**Good**:
```bash
cd "$HOME/code/python"
```

**Bad**:
```bash
cd $HOME/code/python                            # Breaks if $HOME has spaces
```

### 2. Use `-p` with `mkdir`

**Good**:
```bash
mkdir -p path/to/directory                      # Creates all needed directories
```

**Bad**:
```bash
mkdir path/to/directory                         # Fails if path/to doesn't exist
```

### 3. Check Before Removing

**Good**:
```bash
[ -f file.txt ] && rm file.txt || echo "File doesn't exist"
```

**Bad**:
```bash
rm file.txt                                     # Error if file doesn't exist
```

### 4. Use `test` or `[ ]` for Conditions

Both are equivalent:
```bash
test -f file.txt
[ -f file.txt ]
```

Note: `[ ]` requires spaces around brackets!

### 5. Combine Commands with `&&` and `||`

Chain operations logically:
```bash
cd directory && command1 && command2 || echo "Something failed"
```

### 6. Redirect Errors Appropriately

```bash
command 2>/dev/null                             # Hide errors completely
command 2>&1                                    # Show errors with output
command > output.txt 2>&1                       # Save both to file
```

---

## Common Patterns from This Project

### Pattern 1: Check and Act

```bash
if [ -f file.txt ]; then
    echo "File exists"
else
    echo "File not found"
fi
```

Or shorter:
```bash
[ -f file.txt ] && echo "Exists" || echo "Missing"
```

### Pattern 2: Find and Process

```bash
find . -name "pattern" -exec command {} \;
```

### Pattern 3: Filter and Count

```bash
command | grep "pattern" | wc -l
```

### Pattern 4: Safe Directory Navigation

```bash
cd "$(dirname "$0")"                            # Go to script's directory
```

### Pattern 5: Check Command Availability

```bash
which command >/dev/null 2>&1 && echo "Available" || echo "Not found"
```

---

## Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `cd` | Change directory | `cd ~/code/python` |
| `ls` | List files | `ls -la` |
| `mkdir -p` | Create directory | `mkdir -p dir/subdir` |
| `rm -rf` | Remove (careful!) | `rm -rf directory/` |
| `find` | Search files | `find . -name "*.py"` |
| `grep` | Search text | `grep "pattern" file.txt` |
| `cat` | Show file | `cat file.txt` |
| `head/tail` | View parts | `head -20 file.txt` |
| `wc -l` | Count lines | `wc -l file.txt` |
| `du -sh` | Disk usage | `du -sh directory/` |
| `which` | Find command | `which python3` |
| `test -f` | Check file | `test -f file.txt` |
| `\|` | Pipe | `ls \| grep .py` |
| `>` | Redirect | `command > file.txt` |
| `&&` | And | `cmd1 && cmd2` |
| `\|\|` | Or | `cmd1 \|\| cmd2` |
| `$()` | Substitution | `echo $(date)` |

---

## Learning Path

1. **Start with basics**: `cd`, `ls`, `pwd`, `cat`
2. **Learn file operations**: `mkdir`, `rm`, `cp`, `mv`
3. **Master search**: `find`, `grep`
4. **Understand pipes**: `|`, `>`, `>>`
5. **Use conditionals**: `&&`, `||`, `test`
6. **Practice combinations**: Chain commands together

---

**Remember**: The best way to learn bash is by doing! Try modifying these examples and see what happens. Always test commands in a safe directory first, especially ones that modify or delete files.

