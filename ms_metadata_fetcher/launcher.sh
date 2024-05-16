#!/bin/bash

# To obtain the actual path to ms_metadata_fetcher dir
p=$(dirname $(dirname $(realpath $0)))

path_to_scripts="${p}/ms_metadata_fetcher/"

# Function to run a script and check its return code
run_script() {
    script_name=$1
    echo "Running $script_name"
    python3 "${path_to_scripts}${script_name}.py"
    if [ $? -ne 0 ]; then
        echo "$script_name failed"
        exit 1
    fi
}

# Run fetcher
run_script "metadata_fetcher"

# Run emi id extracter
run_script "file_manager"
