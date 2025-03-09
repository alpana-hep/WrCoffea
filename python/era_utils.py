import logging

# Mapping of eras to dataset paths
ERA_MAPPING = {
    "RunIISummer20UL16": {"run": "RunII", "year": "2016"},
    "RunIISummer20UL17": {"run": "RunII", "year": "2017"},
    "RunIISummer20UL18": {"run": "RunII", "year": "2018"},
    "Run3Summer22": {"run": "Run3", "year": "2022"},
    "Run3Summer22EE": {"run": "Run3", "year": "2022"},
    "Run3Summer23": {"run": "Run3", "year": "2023"},
    "Run3Summer23BPix": {"run": "Run3", "year": "2023"},
}

def get_era_details(era):
    """
    Retrieves the 'run' and 'year' associated with a given era.

    Args:
        era (str): The era name (e.g., "RunIISummer20UL18").

    Returns:
        tuple: (run, year) if era is found, otherwise logs an error and exits.
    """
    mapping = ERA_MAPPING.get(era)
    if mapping is None:
        logging.error(f"Unsupported era: {era}")
        exit(1)
    
    return mapping["run"], mapping["year"], era
