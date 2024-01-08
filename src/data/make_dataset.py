# -*- coding: utf-8 -*-
import click
import logging
from roboflow import Roboflow
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import os

# @click.command()
# @click.argument('input_filepath', type=click.Path(exists=True))
# @click.argument('output_filepath', type=click.Path())
def main(rf_data_version: int=3, data_format: str = "yolov8"):
    """ Grabs data from RoboFlow, if not already downloaded to the 
        current directory.
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # Pull data from roboflow
    rf = Roboflow(api_key=os.environ.get("RF_API_KEY"))
    project = rf.workspace(os.environ.get("RF_WORKSPACE")).project(os.environ.get("RF_PROJECT"))

    dataset = project.version(rf_data_version).download(data_format, location=str(project_dir))
    print(dataset.location)

# @click.command()
# @click.argument('input_filepath', type=click.Path(exists=True))
# @click.argument('output_filepath', type=click.Path())
# def main_given(input_filepath, output_filepath):
#     """ Grabs data from RoboFlow, if not already downloaded to the 
#         current directory.
    
    
    
#         Runs data processing scripts to turn raw data from (../raw) into
#         cleaned data ready to be analyzed (saved in ../processed).
#     """
#     logger = logging.getLogger(__name__)
#     logger.info('making final data set from raw data')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # Add roboflow data to the 'external' folder
    project_dir = project_dir.joinpath("data/external")

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())
    main()
