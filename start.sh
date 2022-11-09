# Check conda 
echo "Checking conda.."
if ! command -v conda &> /dev/null
then
    echo "Conda could not be found. Install conda at https://www.anaconda.com"
    exit
fi

# Check if conda env exists
find_in_conda_env(){
    conda env list | grep "${@}" >/dev/null 2>/dev/null
}

echo "Checking conda env.."
if find_in_conda_env ".*MEMCACHE.*" ; then
    echo "Conda env detected, activating..."
    conda info | egrep "conda version|active environment"
    conda activate MEMCACHE
else 
    echo "Conda env doesn't exist."
    echo "Importing conda env..."
    conda info | egrep "conda version|active environment"
    conda env create -f environment.yml
    if find_in_conda_env ".*MEMCACHE.*" ; then
        echo "Conda env installed, activating..."
        conda info | egrep "conda version|active environment"
        conda activate MEMCACHE
    else
        echo "Failed to import conda env, exit."
        exit
    fi
fi

echo "You are good to go. Launching instance.."
sleep 1s

# Lauch instanc
python3 /home/ubuntu/Node_server/1779_A2_NodeServer/run.py
