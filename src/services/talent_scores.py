"""Shared score loading for Streamlit pages."""
import streamlit as st

from src.data.loader import get_feature_table
from src.scoring.calculator import calculate_raw_scores
from src.scoring.normalizer import normalize


@st.cache_data
def load_scores():
    features = get_feature_table()
    raw = calculate_raw_scores(features)
    scores = normalize(raw)
    return features, scores
