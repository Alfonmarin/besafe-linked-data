
import streamlit as st
import pandas as pd
import sys
import os
# Añadir /src al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from queries.internal import get_measurements

st.title("BeSafe – Calidad del Aire (Demo Inicial)")

data = get_measurements()
df = pd.DataFrame(data)

st.subheader("Primeras mediciones del RDF")
st.dataframe(df.head(20))
