import os
import cv2
import pandas as pd
import yaml

def format_preprocessing_dictionary(augmentation_dict):
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
    with open(yaml_file, 'r') as file:
        labels_data = yaml.load(file, Loader=yaml.FullLoader)
        return labels_data['names']

def calculate_label_counts(label_file, all_labels):
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
    splits = ['train', 'valid', 'test']  # Default folders
    with open(data_folder + '/data.yaml') as file:
        all_labels = yaml.safe_load(file)['names']

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