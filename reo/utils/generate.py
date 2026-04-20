import os
# Define the folders and file extensions to exclude
excluded_folders = {
    '.venv',
    '.vscode',
    '__pycache__',
    '.git',
    '.idea',
    'venv',
    '.config',
    '.local',
    '.cache',
    'node_modules',
    'build',
    'dist',
    'env',
    'logs',
    'logs_old',
    'logs_new',
    'logs_archive'
}
excluded_extensions = {'.log'}

def generate_tree(directory, prefix=''):
    entries = []
    dirs = []
    files = []

    # Using os.scandir() for more efficient directory traversal
    with os.scandir(directory) as it:
        for entry in sorted(it, key=lambda e: e.name.lower()):
            if entry.name in excluded_folders:
                continue
            if entry.is_dir(follow_symlinks=False):
                dirs.append(entry)
            elif not any(entry.name.endswith(ext) for ext in excluded_extensions):
                files.append(entry)

    # Process directories first
    for i, entry in enumerate(dirs):
        connector = '└── ' if i == len(dirs) - 1 and not files else '├── '
        entries.append(f"{prefix}{connector}{entry.name}")
        sub_prefix = '    ' if i == len(dirs) - 1 and not files else '│   '
        entries.extend(generate_tree(entry.path, prefix + sub_prefix))

    # Process files last
    for i, entry in enumerate(files):
        connector = '└── ' if i == len(files) - 1 else '├── '
        entries.append(f"{prefix}{connector}{entry.name}")
    
    return entries

def generate_directory_tree_string(start_directory='.'):
    # Generate the tree structure
    tree_structure = generate_tree(start_directory)
    
    # Join the tree structure into a single string with line breaks
    return '\n'.join(tree_structure)

def generate_directory_tree_string_split_text(max_length):
    """Split text into chunks without breaking lines."""
    text = generate_directory_tree_string()
    lines = text.split('\n')
    chunks = []
    current_chunk = []

    current_length = 0
    for line in lines:
        if current_length + len(line) + 1 > max_length:  # +1 for the newline character
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_length = 0
        
        current_chunk.append(line)
        current_length += len(line) + 1  # +1 for the newline character
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks