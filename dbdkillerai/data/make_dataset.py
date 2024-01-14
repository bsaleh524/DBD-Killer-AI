# -*- coding: utf-8 -*-
import click
import logging
from roboflow import Roboflow
from roboflow.core import project, dataset
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import os
from typing import Tuple

# @click.command()
# @click.argument('input_filepath', type=click.Path(exists=True))
# @click.argument('output_filepath', type=click.Path())
def roboflow_connect() -> Tuple[
    Roboflow, project.Project]:
    """ Grabs data from RoboFlow, if not already downloaded to the 
        current directory.
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # Pull data from roboflow
    rf_conn = Roboflow(api_key=os.environ.get("RF_API_KEY"))
    rf_project = rf_conn.workspace(os.getenv("RF_WORKSPACE")).project(os.getenv("RF_PROJECT"))
    return rf_conn, rf_project

def roboflow_download(rf_project, rf_data_version: str="3",
                      data_format: str = "yolov8", project_dir: str = "data/external",
                      overwrite: bool=False) -> dataset.Dataset:
    
    # Save in correct project directory
    project_dir = str(project_dir) + "/" + rf_project.version(rf_data_version).id
    if not os.path.exists(project_dir):
        # If not, create it
        os.makedirs(project_dir)
    
    rf_dataset = rf_project.version(rf_data_version).download(model_format=data_format,
                                                              location=str(project_dir),
                                                              overwrite=overwrite)
    return rf_dataset



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
    grab_roboflow_data()
