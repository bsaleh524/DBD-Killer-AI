import os
import cv2
import pandas as pd
import yaml

def format_preprocessing_dictionary(augmentation_dict):
    """Print the preprocessing that took place on the data from Roboflow."""
    formatted_text = ""
    
    for key, value in augmentation_dict.items():
        formatted_text += f"**{key}:**\n"
        
        if isinstance(value, dict):
            formatted_text += format_nested_dict(value, level=1)
        else:
            formatted_text += f"{value}\n"
        
        formatted_text += "\n"
    
    return formatted_text

def format_nested_dict(nested_dict, level):
    """Take a nested dictionary and print it out with indentations after
    each descending key."""
    formatted_text = ""
    
    for key, value in nested_dict.items():
        indentation = "    " * level
        formatted_text += f"{indentation}**{key}:** "
        
        if isinstance(value, dict):
            formatted_text += "\n" + format_nested_dict(value, level + 1)
        else:
            formatted_text += f"{value}\n"
    
    return formatted_text

def load_labels_from_yaml(yaml_file):
    """Get the labels under the dataset version using the yaml file."""
    with open(yaml_file, 'r') as file:
        labels_data = yaml.load(file, Loader=yaml.FullLoader)
        return labels_data['names']

def calculate_label_counts(label_file, all_labels):
    """Get the counts of all labels from the dataset."""
    label_counts = {label: 0 for label in all_labels}

    with open(label_file, 'r') as label_file:
        lines = label_file.readlines()
        for line in lines:
            # Split the line and get the class index
            parts = line.strip().split(' ')
            if len(parts) > 0 and parts[0].isdigit():
                class_index = int(parts[0])
                class_label = all_labels[class_index]
                label_counts[class_label] += 1
        return label_counts

def calculate_image_properties(image_path, label_path, all_labels):
    """Grab and calculate Height, Width, Aspect Ratio, and the counts
    of all labels."""
    # Read image to get dimensions
    img = cv2.imread(image_path)
    height, width, _ = img.shape
    
    # Calculate aspect ratio
    aspect_ratio = width / height

    # Count labels in the label file
    label_counts = calculate_label_counts(label_path, all_labels)

    return {
        'Width': width,
        'Height': height,
        'AspectRatio': aspect_ratio,
        **label_counts  # Add label counts to the result
    }

def process_yolov8_dataset(data_folder):
    """Create a dataframe of all images from a roboflow dataset,
    including properties."""
    splits = ['train', 'valid', 'test']  # Default folders
    # with open(data_folder + '/data.yaml') as file:
    #     all_labels = yaml.safe_load(file)['names']

    all_labels = load_labels_from_yaml(data_folder + '/data.yaml')

    data_columns = ['Split', 'Image', 'Width', 'Height', 'AspectRatio'] + all_labels
    data = {col: [] for col in data_columns}

    for split in splits:
        images_folder = os.path.join(data_folder, split, 'images')
        labels_folder = os.path.join(data_folder, split, 'labels')

        image_files = [f for f in os.listdir(images_folder) if f.endswith('.jpg') or f.endswith('.png')]
        for image_file in image_files:
            image_path = os.path.join(images_folder, image_file)
            label_file = os.path.join(labels_folder, image_file.replace('.jpg', '.txt').replace('.png', '.txt'))

            image_properties = calculate_image_properties(image_path, label_file, all_labels)

            data['Split'].append(split.capitalize())
            data['Image'].append(image_file)
            data['Width'].append(image_properties['Width'])
            data['Height'].append(image_properties['Height'])
            data['AspectRatio'].append(image_properties['AspectRatio'])

            for label in all_labels:
                data[label].append(image_properties[label])

    df = pd.DataFrame(data)
    return df

#TODO: process_'model'_dataset
#TODO: process_'model'_dataset

def get_data_value_from_args_yaml(run_dir):
    """Grab arguments used from a previous model run."""
    args_path = os.path.join(run_dir, 'args.yaml')
    
    if os.path.exists(args_path):
        with open(args_path, 'r') as args_file:
            args_data = yaml.safe_load(args_file)
            return args_data.get('data')

    return None

def get_best_model_info(run_dir):
    """For the given model, pull information from the argument file."""
    results_path = os.path.join(run_dir, 'results.csv')
    weights_path = os.path.join(run_dir,  'weights', 'best.pt')
    args_yaml_path = os.path.join(run_dir, 'args.yaml')

    if os.path.exists(results_path) and os.path.exists(weights_path) and os.path.exists(args_yaml_path):
        # Read the results.csv file
        results_df = pd.read_csv(results_path)

        # Try to find the column with mAP (with or without "(B)")
        mAP_column_candidates = [col for col in results_df.columns if 'metrics/mAP50' in col]

        if mAP_column_candidates:
            mAP_column = mAP_column_candidates[0]

            # Find the row with the highest mAP
            best_model_row = results_df[results_df[mAP_column] == results_df[mAP_column].max()]

            if not best_model_row.empty:
                best_model_info = {
                    'model_folder': run_dir,
                    'weights_path': weights_path,
                    'mAP': best_model_row[mAP_column].values[0],
                    'args_yaml_path': args_yaml_path
                }
                return best_model_info

    return None

def find_best_model(runs_directory, folder_type="train",
                    target_data_value: str = "deadbydaylightkillerai/killer_ai_object_detection/5"):
    """Based on a dataset, pull the best weights of a yolo model trained on taht dataset.
    The best model is grabbed by acquiring the highest mAP. Directly correlates with
    how ultralytics generates the best.pt weights."""
    run_dirs = [d for d in os.listdir(runs_directory) if os.path.isdir(os.path.join(runs_directory, d)) and folder_type in d.lower()]
    
    filtered_run_dirs = []

    # Filter run_dirs based on target_data_value
    for run_dir in run_dirs:
        data_value = get_data_value_from_args_yaml(os.path.join(runs_directory, run_dir))
        if data_value is not None and target_data_value in data_value:
            filtered_run_dirs.append(run_dir)

    best_model_info = None

    for run_dir in filtered_run_dirs:
        model_info = get_best_model_info(os.path.join(runs_directory, run_dir))
        if model_info is not None:
            if best_model_info is None or model_info['mAP'] > best_model_info['mAP']:
                best_model_info = model_info
    if best_model_info is not None:
        print(f"Model Folder: {best_model_info['model_folder']}")
        print(f"Weights Path: {best_model_info['weights_path']}")
        print(f"mAP: {best_model_info['mAP']}")
    else:
        print(f"No models trained on dataset {target_data_value[-1]}")
    return best_model_info
