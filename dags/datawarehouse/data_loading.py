from datetime import date
import json
import logging

logger = logging.getLogger(__name__)

def load_data():

    file_path = f"./data/YT_data_{date.today()}.json"

    try:
        logger.info(f"Traitement du fichier: YT_data_{date.today()}")

        with open(file_path, 'r') as raw_data:
            data = json.load(raw_data)

        return data
    except FileNotFoundError:
        logger.error(f"Le fichier {file_path} n'existe pas.")
        raise
    except json.JSONDecodeError:
        logger.error(f"Erreur lors du décodage du fichier JSON {file_path}.")
        raise