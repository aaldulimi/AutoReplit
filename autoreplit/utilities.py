import subprocess
import os
import shutil

def format_folder(folder):
    return "'.' " + "'{}'".format(folder.replace(' ', r' ').replace('/', r' '))


def flatten_directory(repl_name: str = 'ar', source_dir: str = '.'):
    subprocess.run(f'mkdir {repl_name}', shell=True)

    folders_list = []
    to_move = []

    for root, _, files in os.walk(source_dir):
        if root == f'./{repl_name}':
            continue

        for file_name in files:
            file_path = os.path.join(root, file_name)

            if "__pycache__" in file_path:
                continue
            
            if ".venv" in file_path:
                continue
            
            relative_path = os.path.relpath(root, source_dir)
            new_file_name = file_name

            if relative_path != ".":
                relative_path = "!" + "!".join(relative_path.split(os.path.sep)) + "!"
                new_file_name = relative_path + file_name

            target_file_path = os.path.join(repl_name, new_file_name)

            to_move.append((file_path, target_file_path))


        folder_path = os.path.relpath(root, source_dir)
        if folder_path and ".venv" not in folder_path:
            folders_list.append(folder_path)

    for file_path, target_file_path in to_move:
        shutil.copy2(file_path, target_file_path)

    
    folders_list.remove('.')  
    folders_str = '\n\t'.join(format_folder(folder) for folder in folders_list)

    bash_str = f"""
#!/bin/bash
folders=(
\t{folders_str}
)   
"""
    with open(f'{repl_name}/move.sh', 'w') as file:
        file.write(bash_str + BASH_SCRIPT)

    return repl_name


def all_files(folder: str = './ar'):
    file_count = 0
    ignore = [
        'venv',
        '.venv',
        'poetry.lock',
        'pyproject.toml',
        '.python-version',
        '__pycache__',
    ]

    files = []
    for path in os.listdir(folder):
        if path in ignore:
            continue
        full_path = os.path.join(folder, path)

        if os.path.isfile(full_path):
            files.append(f"{folder}/{path}")
            file_count += 1

    return files, file_count



BASH_SCRIPT = """    


convert_to_path() {
    local path=""
    local first=true

    # Loop through the space-separated path elements and concatenate with slashes
    for folder in $@; do
        if [ "$first" = true ]; then
            if [ "$folder" = "." ]; then
                path="."
            else
                path="$folder"
            fi
            first=false
        else
            path="$path/$folder"
        fi
    done

    echo "$path"
}




# Iterate through the folders list and convert to paths
for ((i = 0; i < ${#folders[@]}; i+=2)); do
    path=$(convert_to_path "${folders[$i]}" "${folders[$i+1]}")
    echo "$path" 
    mkdir -p "$path"
done



move_file() { 
  local source_file="$1"
  local target_file="$2"

  # Remove the leading slash if present in target_file
  if [[ "$target_file" == /* ]]; then
    target_file="${target_file#"/"}"
  fi

  echo "Moving $source_file to $target_file"
  mv "$source_file" "$target_file"
}

# Set the separator for folder structure
separator="!"


# Loop through the files in the current directory
for file in *; do
  # Check if the file name contains the separator
  if [[ "$file" == *"$separator"* ]]; then
    # Extract the target directory path
    target_dir=$(dirname "${file//$separator//}")
        
    # Move the file to the correct location
    move_file "$file" "${file//$separator//}"
  fi
done


sleep 5
rm "$0"

"""