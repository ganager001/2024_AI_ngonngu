import json,os
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
from datetime import datetime
from collections import defaultdict
from underthesea import word_tokenize, pos_tag

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

def calculate_hotness_and_factors(group, df):
    total_topics = df['cluster'].nunique()
    all_websites = df['website']
    all_times = df['time']

    K = len(group['website'].unique())
    C = total_topics
    
    hotness = 0
    factors = []
    for website in group['website'].unique():
        website_group = group[group['website'] == website]
        Di = len(website_group)
        Ni = len(all_websites[all_websites == website])
        
        sum_Dji_squared = sum(len(df[(df['website'] == website) & (df['cluster'] == j)])**2 for j in df['cluster'].unique())
        
        factor = (Di / np.sqrt(sum_Dji_squared)) * np.exp(Di/Ni) * 1
        hotness += factor
        factors.append({
            'Website': website,
            'Di': Di,
            'Ni': Ni,
            'sum_Dji_squared': sum_Dji_squared,
            'Di/sqrt(sum_Dji_squared)': Di / np.sqrt(sum_Dji_squared),
            'exp(Di/Ni)': np.exp(Di/Ni),
            'Wi': 1,
            'Factor': factor
        })
    
    M = len(group['time'].unique())
    m = len(all_times.unique())
    
    H1 = hotness * (M/m)
    return H1, factors, K, C, M, m

def calculate_H_factors(group, total_df):
    f_j_sum = group['total_likes'].sum()
    f_j_squared_sum_all = sum((total_df.groupby('cluster')['total_likes'].sum())**2)
    Hl = f_j_sum / np.sqrt(f_j_squared_sum_all)
    
    c_j_sum = group['total_comments'].sum()
    c_j_squared_sum_all = sum((total_df.groupby('cluster')['total_comments'].sum())**2)
    Hc = c_j_sum / np.sqrt(c_j_squared_sum_all)
    
    Hs = 0
    
    return Hl, Hc, Hs

def calculate_H2(group, total_df):
    Hl, Hc, Hs = calculate_H_factors(group, total_df)
    H2 = (Hl + 2*Hc + 4*Hs) / 7
    return H2, Hl, Hc, Hs

def load_data(start_date,end_date):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, '..', 'common', 'data_gan_nhan.json')
    data_file = os.path.abspath(data_file)
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    filtered_data = []

    if start_date:
        start_date = datetime.strptime(start_date, '%m/%d/%Y')
    if end_date:
        end_date = datetime.strptime(end_date, '%m/%d/%Y')

    for item in data:
        item_date_str = item.get('time')  # Giả sử có trường 'date'
        if item_date_str:
            try:
                item_date = datetime.strptime(item_date_str, '%d/%m/%Y')
                if start_date and end_date:
                    if start_date <= item_date <= end_date:
                        filtered_data.append(item)
            except:
                pass
                continue
 
    return filtered_data

def calculate_hotness(start_date,end_date):
    # Đọc dữ liệu JSON
    data = load_data(start_date,end_date)

    # Xử lý dữ liệu
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

    # Tạo DataFrame
    df = pd.DataFrame([{
        'id': item.get('id', i),
        'website': item.get('website', ''),
        'title': clean_title(item['title']),
        'time': format_date(item.get('time', '')),
        'url': item.get('url', ''),
        'category': item.get('category', ''),
        'total_comments': safe_int(item.get('total_comments', 0)),
        'total_likes': safe_int(item.get('total_likes', 0)),
        'processed_text': process_text(f"{item['category']} {item['title']} {item['description']} {item['content']}")
    } for i, item in enumerate(data)])

    # Tính TF-IDF và phân cụm
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['processed_text'])

    similarity_matrix = cosine_similarity(tfidf_matrix)
    distance_matrix = 1 - similarity_matrix
    distance_matrix = np.clip(distance_matrix, 0, None)

    k = min(int(np.log(len(df))), distance_matrix.shape[1] - 1)
    optimal_eps = find_optimal_eps(distance_matrix, k)
    min_pts = min(2 * tfidf_matrix.shape[1] - 1, 5)

    dbscan = DBSCAN(eps=optimal_eps, min_samples=min_pts, metric='precomputed')
    df['cluster'] = dbscan.fit_predict(distance_matrix)
    df['cluster'] = df['cluster'].apply(lambda x: int(x) + 1 if x != -1 else -1)

    # Tính độ nóng cho từng chủ đề
    results = []
    for topic, group in df[df['cluster'] != -1].groupby('cluster'):
        H1, factors, K, C, M, m = calculate_hotness_and_factors(group, df)
        H2, Hl, Hc, Hs = calculate_H2(group, df)
        H = H1 + H2
        
        # Tạo danh sách từ khóa cho mỗi cụm
        tfidf_cluster = tfidf_matrix[df['cluster'] == topic]
        tfidf_sum = tfidf_cluster.sum(axis=0)
        top_term_indices = tfidf_sum.argsort()[0, -10:][::-1]
        top_terms = [vectorizer.get_feature_names_out()[i] for i in top_term_indices.tolist()[0]]
        keywords = ', '.join(top_terms)
        
        results.append({
            'Cum_chu_de': topic,
            'H': round(H, 3),
            'H1': round(H1, 3),
            'H2': round(H2, 3),
            'Hl': round(Hl, 3),
            'Hc': round(Hc, 3),
            'Hs': round(Hs, 3),
            'Factors': factors,
            'K': K,
            'C': C,
            'M': M,
            'm': m,
            'So_bai_viet': len(group),
            'Tong_likes': group['total_likes'].sum(),
            'Tong_comments': group['total_comments'].sum(),
            'Keywords': keywords,
        })

    # Sắp xếp kết quả theo H giảm dần
    results_df = pd.DataFrame(results).sort_values('H', ascending=False)

    return results_df