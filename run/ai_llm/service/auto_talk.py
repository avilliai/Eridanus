from typing import List
import numpy as np

from framework_common.utils.install_and_import import install_and_import
from typing import List

import numpy as np

from framework_common.utils.install_and_import import install_and_import

sklearn=install_and_import("scikit-learn","sklearn")

jieba=install_and_import("jieba")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import gc
from collections import Counter


def clean_text(text: str) -> str:
    """
    去特殊字符和数字
    """
    text = re.sub(r'[^\u4e00-\u9fff\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    return text

def calculate_entropy(tokens: List[str]) -> float:
    """
    信息熵 H(t) = -∑_{w ∈ W} p(w) log_2 p(w)，p(w) = count(w) / ∑_{w' ∈ W} count(w')
    """
    if not tokens:
        return 0.0
    counter = Counter(tokens)
    total = len(tokens)
    entropy = -sum((count / total) * np.log2(count / total) for count in counter.values())
    return entropy

def tokenize(text: str) -> List[str]:
    text = clean_text(text.lower().strip())
    if re.search(r'[\u4e00-\u9fff]', text) and not re.search(r'[\u3040-\u30ff\u31f0-\u31ff]', text):
        # 中
        tokens = list(jieba.cut(text, cut_all=False))
    elif re.search(r'[\u3040-\u30ff\u31f0-\u31ff]', text):
        # 日
        tokens = re.findall(r'[\u3040-\u30ff\u31f0-\u31ff]+', text)
    else:
        # 别的
        tokens = re.findall(r'\b\w+\b', text)
    return tokens

def calculate_time_weight(index: int, total: int) -> float:
    """
    窗口权重
    """
    return 1 + (total - index) * 0.1

async def check_message_similarity(
    input_str: str,
    message_list: List[str],
    similarity_threshold= 0.3,
    frequency_threshold= 0.15,
    min_list_size: int = 10,
    entropy_threshold: float = 2.0
) -> bool:
    def convert_number(num):
        if isinstance(num, int):
            return num / 100.0
        elif isinstance(num, float):
            return num
    similarity_threshold = convert_number(similarity_threshold)
    frequency_threshold = convert_number(frequency_threshold)
    try:
        #print(message_list)
        # 检查消息列表长度
        if len(message_list) < min_list_size:
            #print(f"Message list size {len(message_list)} < {min_list_size}")
            return False

        if not message_list:
            #print("No valid messages to compare")
            return False

        # 分词输入字符串
        input_tokens = tokenize(input_str)
        input_length = len(input_str)

        # 动态熵阈值
        if re.search(r'[\u4e00-\u9fff]', input_str) and not re.search(r'[\u3040-\u30ff\u31f0-\u31ff]', input_str):
            # 中
            entropy_threshold = 1.5
        elif re.search(r'[\u3040-\u30ff\u31f0-\u31ff]', input_str):
            # 日
            entropy_threshold = 2.0
        else:
            # 别的
            entropy_threshold = 2.5

        # 分词
        tokenized_texts = []
        entropies = []
        time_weights = []
        total_messages = len(message_list)
        for i, text in enumerate(message_list):
            tokens = tokenize(text)
            tokenized_texts.append(' '.join(tokens))
            entropy = calculate_entropy(tokens)
            entropies.append(entropy)
            time_weight = calculate_time_weight(i, total_messages)
            time_weights.append(time_weight)

        # TF-IDF 词向量：TF-IDF(w, t, T) = TF(w, t) * IDF(w, T)
        # TF(w, t) = count(w, t) / ∑_{w' ∈ t} count(w', t)
        # IDF(w, T) = log |T| / |{t ∈ T : w ∈ t}|
        vectorizer = TfidfVectorizer(
            lowercase=True,
            token_pattern=None,
            tokenizer=lambda x: x.split(),
            max_features=min(300, len(set([token for text in tokenized_texts for token in text.split()]))),
            ngram_range=(1, 3),
            stop_words=None
        )
        tfidf_matrix = vectorizer.fit_transform([*tokenized_texts, ' '.join(input_tokens)])

        # 余弦相似度
        input_vector = tfidf_matrix[-1]
        message_vectors = tfidf_matrix[:-1]
        similarities = cosine_similarity(input_vector, message_vectors).flatten()

        # 熵调整和窗口权重
        alpha = 0.3
        adjusted_similarities = [
            sim * (entropy / entropy_threshold) ** alpha * time_weight if entropy > 0 else sim * 0.1 * time_weight
            for sim, entropy, time_weight in zip(similarities, entropies, time_weights)
        ]

        # frequency = ∑_{i=1}^n 1(sim'(s, t_i) ≥ similarity_threshold) / n
        high_similarity_count = np.sum(np.array(adjusted_similarities) >= similarity_threshold)
        similarity_frequency = high_similarity_count / len(message_list)

        #print(
            #f"Similarity frequency: {similarity_frequency:.3f}, Threshold: {frequency_threshold}"
        #)

        del tfidf_matrix, similarities, adjusted_similarities
        gc.collect()

        return similarity_frequency >= frequency_threshold

    except Exception as e:
        #print(f"Error in check_message_similarity: {e}")
        return False
