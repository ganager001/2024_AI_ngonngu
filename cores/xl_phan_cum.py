import json
import re
import numpy as np
# import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
from underthesea import word_tokenize, pos_tag
import base64
from io import BytesIO

# custommers/cluster/clustering_utils.py

# Thêm các import cần thiết
from django.conf import settings
import os



def replace_phrases(text, phrase_dict):
    for phrase, token in phrase_dict.items():
        text = re.sub(re.escape(phrase), token, text)
    return text

def create_phrase_dict(tagged_category):
    phrase_dict = {}
    for phrase in tagged_category:
        phrase_text = ' '.join([word for word, tag in phrase])
        token = phrase_text.replace(' ', '_')
        phrase_dict[phrase_text] = token
    return phrase_dict

def process_category(category):
    parts = [part.strip() for part in category.split('>')]
    tagged_parts = [pos_tag(word_tokenize(part, format="text")) for part in parts]
    return tagged_parts

def process_text(text):
    word_tags = text.split()
    processed_words = [word.split('|')[0].lower() for word in word_tags if '|' not in word or word.split('|')[1] not in ['CH', 'T', 'Cc', 'E', 'R', 'L', 'P']]
    return ' '.join(processed_words)

def find_optimal_eps(distances, k):
    sorted_distances = np.sort(distances, axis=1)
    k_distances = sorted_distances[:, k]
    return np.mean(k_distances)

def plot_clusters(tfidf_matrix, clusters):
    pca = PCA(n_components=2)
    reduced_data = pca.fit_transform(tfidf_matrix.toarray())
    
    unique_clusters = set(clusters)
    num_clusters = len(unique_clusters) - 1 if -1 in unique_clusters else len(unique_clusters)
    colors = plt.cm.get_cmap('tab20', num_clusters)

    plt.figure(figsize=(12, 10))
    
    for cluster in unique_clusters:
        if cluster == -1:
            color = 'lightgray'
            label = 'Nhiễu'
            alpha = 0.3
        else:
            color = colors(cluster)
            label = f'Cụm {cluster+1}'
            alpha = 1

        cluster_points = reduced_data[clusters == cluster]
        plt.scatter(cluster_points[:, 0], cluster_points[:, 1], c=[color], label=label, s=30, alpha=alpha)

    plt.xlabel('Thành phần PCA 1', fontsize=10)
    plt.ylabel('Thành phần PCA 2', fontsize=10)
    plt.title('Kết quả phân cụm bằng thuật toán DBSCAN cải tiến', fontsize=14)
    plt.legend(fontsize=8, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return image_base64

def format_date(date_string):
    try:
        for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
            try:
                date_object = datetime.strptime(date_string, fmt)
                return date_object.strftime("%d/%m/%Y")
            except ValueError:
                continue
        date_object = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_object.strftime("%d/%m/%Y")
    except:
        return date_string

def clean_title(title):
    words = [word.split('|')[0].replace('_', ' ') for word in title.split()]
    cleaned_title = ' '.join(words)
    cleaned_title = re.sub(r'\s+([\'"])', r'\1', cleaned_title)
    cleaned_title = re.sub(r'([\'"])\s+', r'\1', cleaned_title)
    cleaned_title = re.sub(r'\s+([.,!?])', r'\1', cleaned_title)
    return cleaned_title

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def perform_clustering(data):
    print("Starting perform_clustering.....")
    try:
        for record in data:
            if 'category' in record:
                tagged_category = process_category(record['category'])
                phrase_dict = create_phrase_dict(tagged_category)
                
                for key in ['title', 'content', 'description']:
                    if key in record:
                        record[key] = replace_phrases(record[key], phrase_dict)
                
                tagged_category_str = ' > '.join([' '.join([f"{word}|{tag}" for word, tag in part]) for part in tagged_category])
                tagged_category_str = tagged_category_str.replace(' > ', ' >|CH ')
                record['category'] = tagged_category_str

            processed_texts = [process_text(f"{item['category']} {item['title']} {item['description']} {item['content']}") for item in data]

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(processed_texts)

            similarity_matrix = cosine_similarity(tfidf_matrix)
            distance_matrix = 1 - similarity_matrix
            distance_matrix = np.clip(distance_matrix, 0, None)

            k = min(int(np.log(len(processed_texts))), distance_matrix.shape[1] - 1)
            optimal_eps = find_optimal_eps(distance_matrix, k)
            try:
                min_pts = min(2 * tfidf_matrix.shape[1] - 1, 5)
            except:
                min_pts = 0

            dbscan = DBSCAN(eps=optimal_eps, min_samples=min_pts, metric='precomputed')
            clusters = dbscan.fit_predict(distance_matrix)

            plot_base64 = plot_clusters(tfidf_matrix, clusters)

            cluster_results = []
            cluster_titles = defaultdict(list)
            cluster_ids = defaultdict(list)

            for i, (item, cluster) in enumerate(zip(data, clusters)):
                if cluster == -1:
                    continue
                
                clean_title_text = clean_title(item['title'])
                cluster_titles[cluster].append(clean_title_text)
                cluster_ids[cluster].append(item.get('id', i))

            for cluster in sorted(cluster_titles.keys()):
                titles = [f"{i+1}. {title}" for i, title in enumerate(cluster_titles[cluster])]
                titles_str = '\n'.join(titles)
                
                cluster_results.append({
                    "cluster": f"Cụm chủ đề {cluster + 1}",
                    "titles": titles_str,
                    "IDs": cluster_ids[cluster]
                })

            results = []
            for i, (item, cluster) in enumerate(zip(data, clusters)):
                results.append({
                    'id': item.get('id', i),
                    'website': item.get('website', ''),
                    'title': clean_title(item['title']),
                    'time': format_date(item.get('time', '')),
                    'cluster': int(cluster) + 1 if cluster != -1 else -1,
                    'url': item.get('url', ''),
                    'category': item.get('category', ''),
                    'total_comments': safe_int(item.get('total_comments', 0)),
                    'total_likes': safe_int(item.get('total_likes', 0))
                })
            try:
                num_noise = int(np.sum(clusters == -1))
            except:
                num_noise = 0

            try:
                num_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
            except:
                num_clusters = 0

            return {
                'cluster_results': cluster_results,
                'results': results,
                'plot_base64': plot_base64,
                'stats': {
                    'optimal_eps': round(float(optimal_eps),4),
                    'min_pts': min_pts,
                    'num_clusters': num_clusters,
                    'num_noise': num_noise,
                },
            }
    except Exception as e:
        print("An error occurred in perform_clustering:", e)
        return {}
    

# if __name__ == "__main__":
#     output_path = 'common/data_phan_cum.json'
#     with open('common/data_input.json', 'r', encoding='utf-8') as file:
#             data = json.load(file)
#     arr_data = perform_clustering(data)
#     try:
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(arr_data, f, ensure_ascii=False, indent=2)
#     except Exception as e:
#         pass