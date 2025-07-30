"""
Embeddings Handler for Semantic Search and Study Materials
Uses Qwen's text-embedding models for advanced features
"""
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
import dashscope
from dashscope import TextEmbedding
import json
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

class EmbeddingsHandler:
    def __init__(self, api_key: str, cache_dir: str = "./embeddings_cache"):
        self.api_key = api_key
        dashscope.api_key = api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.model = "text-embedding-v3"
        
    def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Get embeddings for text(s) using Qwen's embedding model"""
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            response = TextEmbedding.call(
                model=self.model,
                input=texts
            )
            
            if response.status_code == 200:
                embeddings = []
                for item in response.output['embeddings']:
                    embeddings.append(item['embedding'])
                return np.array(embeddings)
            else:
                logger.error(f"Embedding API error: {response}")
                return np.array([])
                
        except Exception as e:
            logger.error(f"Embeddings error: {e}")
            return np.array([])
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def semantic_search(self, query: str, documents: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Perform semantic search on documents
        
        Args:
            query: Search query
            documents: List of dicts with 'content' and optional 'metadata'
            top_k: Number of top results to return
        """
        # Get query embedding
        query_embedding = self.get_embeddings(query)[0]
        
        # Get document embeddings
        doc_texts = [doc.get('content', '') for doc in documents]
        doc_embeddings = self.get_embeddings(doc_texts)
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(doc_embeddings):
            similarity = self.cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        results = []
        for idx, score in similarities[:top_k]:
            result = documents[idx].copy()
            result['similarity_score'] = float(score)
            results.append(result)
        
        return results
    
    def find_similar_questions(self, question: str, question_bank: List[Dict]) -> List[Dict]:
        """Find similar questions from a question bank"""
        return self.semantic_search(question, question_bank, top_k=5)
    
    def cluster_concepts(self, concepts: List[str], num_clusters: int = 5) -> Dict[int, List[str]]:
        """Cluster related concepts together for study organization"""
        from sklearn.cluster import KMeans
        
        # Get embeddings for all concepts
        embeddings = self.get_embeddings(concepts)
        
        if len(embeddings) == 0:
            return {}
        
        # Perform clustering
        num_clusters = min(num_clusters, len(concepts))
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        clusters = kmeans.fit_predict(embeddings)
        
        # Organize results
        clustered_concepts = {}
        for idx, cluster_id in enumerate(clusters):
            if cluster_id not in clustered_concepts:
                clustered_concepts[cluster_id] = []
            clustered_concepts[cluster_id].append(concepts[idx])
        
        return clustered_concepts
    
    def create_concept_map(self, main_topic: str, subtopics: List[str]) -> Dict:
        """Create a concept map showing relationships between topics"""
        all_topics = [main_topic] + subtopics
        embeddings = self.get_embeddings(all_topics)
        
        if len(embeddings) == 0:
            return {}
        
        main_embedding = embeddings[0]
        relationships = {}
        
        # Calculate relationship strength between main topic and subtopics
        for i, subtopic in enumerate(subtopics):
            similarity = self.cosine_similarity(main_embedding, embeddings[i + 1])
            relationships[subtopic] = {
                'strength': float(similarity),
                'relationship': self._classify_relationship(similarity)
            }
        
        # Find relationships between subtopics
        subtopic_relationships = {}
        for i in range(len(subtopics)):
            for j in range(i + 1, len(subtopics)):
                similarity = self.cosine_similarity(embeddings[i + 1], embeddings[j + 1])
                if similarity > 0.7:  # Strong relationship threshold
                    key = f"{subtopics[i]} <-> {subtopics[j]}"
                    subtopic_relationships[key] = float(similarity)
        
        return {
            'main_topic': main_topic,
            'subtopic_relationships': relationships,
            'cross_relationships': subtopic_relationships
        }
    
    def _classify_relationship(self, similarity: float) -> str:
        """Classify the strength of relationship"""
        if similarity > 0.9:
            return "Very Strong"
        elif similarity > 0.8:
            return "Strong"
        elif similarity > 0.7:
            return "Moderate"
        elif similarity > 0.6:
            return "Weak"
        else:
            return "Very Weak"
    
    def generate_study_path(self, topics: List[str], current_knowledge: List[str]) -> List[str]:
        """Generate optimal study path based on concept relationships"""
        # Get embeddings
        all_concepts = list(set(topics + current_knowledge))
        embeddings = self.get_embeddings(all_concepts)
        
        if len(embeddings) == 0:
            return topics
        
        # Create concept map
        concept_indices = {concept: i for i, concept in enumerate(all_concepts)}
        known_indices = [concept_indices[k] for k in current_knowledge if k in concept_indices]
        topic_indices = [concept_indices[t] for t in topics if t in concept_indices]
        
        # Calculate difficulty based on distance from known concepts
        topic_difficulties = []
        for t_idx in topic_indices:
            if known_indices:
                # Find similarity to closest known concept
                max_similarity = max(
                    self.cosine_similarity(embeddings[t_idx], embeddings[k_idx])
                    for k_idx in known_indices
                )
                difficulty = 1 - max_similarity  # Less similar = more difficult
            else:
                difficulty = 0.5  # Default difficulty
            
            topic_difficulties.append((all_concepts[t_idx], difficulty))
        
        # Sort by difficulty (easiest first)
        topic_difficulties.sort(key=lambda x: x[1])
        
        return [topic for topic, _ in topic_difficulties]

class StudyMaterialsIndex:
    """Index and search study materials using embeddings"""
    
    def __init__(self, embeddings_handler: EmbeddingsHandler):
        self.embeddings_handler = embeddings_handler
        self.materials = []
        self.embeddings = None
        
    def add_material(self, content: str, metadata: Dict):
        """Add study material to index"""
        self.materials.append({
            'content': content,
            'metadata': metadata
        })
        
        # Update embeddings
        if self.embeddings is None:
            self.embeddings = self.embeddings_handler.get_embeddings(content)
        else:
            new_embedding = self.embeddings_handler.get_embeddings(content)
            self.embeddings = np.vstack([self.embeddings, new_embedding])
    
    def search(self, query: str, filters: Optional[Dict] = None, top_k: int = 5) -> List[Dict]:
        """Search study materials"""
        if not self.materials or self.embeddings is None:
            return []
        
        # Apply filters if provided
        filtered_indices = []
        for i, material in enumerate(self.materials):
            if filters:
                match = all(
                    material['metadata'].get(key) == value
                    for key, value in filters.items()
                )
                if match:
                    filtered_indices.append(i)
            else:
                filtered_indices.append(i)
        
        if not filtered_indices:
            return []
        
        # Get query embedding
        query_embedding = self.embeddings_handler.get_embeddings(query)[0]
        
        # Calculate similarities
        similarities = []
        for idx in filtered_indices:
            similarity = self.embeddings_handler.cosine_similarity(
                query_embedding, 
                self.embeddings[idx]
            )
            similarities.append((idx, similarity))
        
        # Sort and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in similarities[:top_k]:
            result = self.materials[idx].copy()
            result['similarity_score'] = float(score)
            results.append(result)
        
        return results