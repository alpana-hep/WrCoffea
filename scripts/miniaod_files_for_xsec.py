import argparse
import os
import subprocess
import time

def run_command_with_retries(command, retries=3, delay=5, timeout=120):
    """
    Runs a subprocess command with retries if it times out.

    Args:
        command (list): The command to run as a list of arguments.
        retries (int): Number of retries allowed.
        delay (int): Delay (in seconds) between retries.
        timeout (int): Timeout (in seconds) for each command execution.

    Returns:
        subprocess.CompletedProcess: The result of the successful command execution.
    """
    attempt = 0
    while attempt < retries:
        try:
            print(f"Attempt {attempt + 1} of {retries}: Running command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                return result  # Return the result if successful
            else:
                print(f"Command failed with return code {result.returncode}: {result.stderr}")
                break  # Stop retrying if the command itself failed
        except subprocess.TimeoutExpired:
            print(f"Command timed out on attempt {attempt + 1}. Retrying in {delay} seconds...")
            attempt += 1
            time.sleep(delay)

    raise RuntimeError(f"Command failed after {retries} retries: {' '.join(command)}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("mc_campaign", type=str, choices=["Run2Summer20UL18", "Run3Summer22", "Run3Summer22EE", "Run3Summer23", "Run3Summer23BPix"], help="Run (e.g., Run2Summer20UL18)")

    # Parse the arguments
    args = parser.parse_args()

    # Build input and output file paths based on the arguments
    input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/miniaod/{args.mc_campaign}_datasets.txt"
    output_dir = f"/uscms/home/bjackson/nobackup/WrCoffea/data/miniaod/{args.mc_campaign}"

    # Load the configuration file
    with open(input_file, 'r') as file:
        dataset_paths = file.readlines()

    us_redirector = "root://cmsxrootd.fnal.gov/"
    for dataset in dataset_paths:
        dataset = dataset.strip()
        print(f'Finding files for {dataset}')

        try:
            # Run the command with retries
            result = run_command_with_retries(
                ['dasgoclient', '-query', f'file dataset={dataset}'],
                retries=5,
                delay=5,
                timeout=10
            )

            files = result.stdout.strip().split('\n')
            prepended_files = [f'{us_redirector}{file}' for file in files]

            dataset_name = dataset.split('/')[1]
            output_txt_path = os.path.join(output_dir, f"{dataset_name}_MINIAOD_files.txt")

            # Write the prepended file paths to the output file
            with open(output_txt_path, 'w') as txt_file:
                for line in prepended_files:
                    txt_file.write(f'{line}\n')

            print(f"File list saved to {output_txt_path}")

        except RuntimeError as e:
            print(f"Error processing dataset {dataset}: {e}")
        except Exception as e:
            print(f"Unexpected error processing dataset {dataset}: {e}")
