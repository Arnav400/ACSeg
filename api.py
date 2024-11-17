# app/api.py

from flask import Blueprint, request, jsonify, send_from_directory
import os
import pandas as pd
from .processing import (
    load_data, clean_data, aggregate_data, remove_outliers,
    scale_data, perform_clustering, assign_clusters,
    map_cluster_labels, generate_visualization
)
import json

api_bp = Blueprint('api', __name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'online_retail_II.xlsx')
IMAGES_PATH = os.path.join(os.path.dirname(__file__), 'static', 'images')

@api_bp.route('/process', methods=['GET'])
def process_data():
    try:
        # Load Data
        df = load_data(DATA_PATH)
        
        # Clean Data
        cleaned_df = clean_data(df)
        
        # Aggregate Data
        aggregated_df = aggregate_data(cleaned_df)
        
        # Remove Outliers
        non_outliers_df, monetary_outliers_df, frequency_outliers_df = remove_outliers(aggregated_df)
        
        # Scale Data
        scaled_data_df = scale_data(non_outliers_df)
        
        # Perform Clustering
        k_values, inertia, silhouette_scores = perform_clustering(scaled_data_df)
        
        # Assign Clusters (for simplicity, choose k=4)
        cluster_labels = assign_clusters(scaled_data_df, n_clusters=4)
        non_outliers_df = map_cluster_labels(non_outliers_df, cluster_labels)
        
        # Map Cluster Labels
        cluster_labels_map = {
            0: "RETAIN",
            1: "RE-ENGAGE",
            2: "NURTURE",
            3: "REWARD",
            -1: "PAMPER",
            -2: "UPSELL",
            -3: "DELIGHT"
        }
        non_outliers_df["ClusterLabel"] = non_outliers_df["Cluster"].map(cluster_labels_map)
        
        # Save processed data to JSON
        processed_data = non_outliers_df.to_dict(orient='records')
        
        return jsonify({
            'status': 'success',
            'data': processed_data,
            'k_values': list(k_values),
            'inertia': inertia,
            'silhouette_scores': silhouette_scores
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/visualization/<plot_type>/<filename>', methods=['GET'])
def get_visualization(plot_type, filename):
    allowed_types = ['hist', 'box']
    if plot_type not in allowed_types:
        return jsonify({'status': 'error', 'message': 'Invalid plot type.'}), 400
    
    return send_from_directory(IMAGES_PATH, filename)

# Additional endpoints can be added here

# app/api.py

@api_bp.route('/generate_plots', methods=['GET'])
def generate_plots():
    try:
        # Load and process data
        df = load_data(DATA_PATH)
        cleaned_df = clean_data(df)
        aggregated_df = aggregate_data(cleaned_df)
        non_outliers_df, monetary_outliers_df, frequency_outliers_df = remove_outliers(aggregated_df)
        scaled_data_df = scale_data(non_outliers_df)
        cluster_labels = assign_clusters(scaled_data_df, n_clusters=4)
        non_outliers_df = map_cluster_labels(non_outliers_df, cluster_labels)
        cluster_labels_map = {
            0: "RETAIN",
            1: "RE-ENGAGE",
            2: "NURTURE",
            3: "REWARD",
            -1: "PAMPER",
            -2: "UPSELL",
            -3: "DELIGHT"
        }
        non_outliers_df["ClusterLabel"] = non_outliers_df["Cluster"].map(cluster_labels_map)
        
        # Generate Histograms
        generate_histogram(non_outliers_df['MonetaryValue'], 'Monetary Value', 'monetary_hist.png')
        generate_histogram(non_outliers_df['Frequency'], 'Frequency', 'frequency_hist.png')
        generate_histogram(non_outliers_df['Recency'], 'Recency', 'recency_hist.png')
        
        # Generate Boxplots
        generate_boxplot(non_outliers_df['MonetaryValue'], 'Monetary Value', 'monetary_box.png')
        generate_boxplot(non_outliers_df['Frequency'], 'Frequency', 'frequency_box.png')
        generate_boxplot(non_outliers_df['Recency'], 'Recency', 'recency_box.png')
        
        return jsonify({'status': 'success', 'message': 'Plots generated successfully.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
