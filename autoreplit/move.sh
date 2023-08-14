
convert_to_path() {
    local path=""
    local first=true

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




for ((i = 0; i < ${#folders[@]}; i+=2)); do
    path=$(convert_to_path "${folders[$i]}" "${folders[$i+1]}")
    echo "$path" 
    mkdir -p "$path"
done



move_file() { 
  local source_file="$1"
  local target_file="$2"

  if [[ "$target_file" == /* ]]; then
    target_file="${target_file#"/"}"
  fi

  echo "Moving $source_file to $target_file"
  mv "$source_file" "$target_file"
}

separator="!"


for file in *; do
  if [[ "$file" == *"$separator"* ]]; then
    target_dir=$(dirname "${file//$separator//}")
        
    move_file "$file" "${file//$separator//}"
  fi
done

sleep 5

rm "$0"