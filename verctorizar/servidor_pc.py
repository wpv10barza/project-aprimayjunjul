from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import requests
import numpy as np
import sys

app = Flask(__name__)

print(f"--- Iniciando Servidor Auditor SAP PM ---")
print(f"Python version: {sys.version}")

# Cargamos el modelo de vectores (se descargará la primera vez)
try:
    print("Cargando modelo de vectorización (all-MiniLM-L6-v2)...")
    vector_model = SentenceTransformer('all-MiniLM-L6-v2') 
except Exception as e:
    print(f"Error cargando modelo: {e}")

LLAMA_API_URL = "http://127.0.0"

@app.route('/ejecutar_auditoria', methods=['POST'])
def ejecutar_auditoria():
    data = request.json
    pregunta = data.get("pregunta", "")
    criterios = data.get("criterios", [])
    evidencia_cruda = data.get("evidencia_cruda", []) 
    
    if not evidencia_cruda:
        return jsonify({"error": "No hay evidencia"}), 400

    # Vectorización y RAG simple
    embeddings_evidencia = vector_model.encode(evidencia_cruda)
    embedding_criterios = vector_model.encode([" ".join(criterios)])
    similitudes = np.dot(embeddings_evidencia, embedding_criterios.T).flatten()
    indices_top = similitudes.argsort()[-3:][::-1] 
    evidencia_filtrada = "\n".join([evidencia_cruda[i] for i in indices_top])

    # Prompt para llama.cpp
    prompt = f"<system>Auditor SAP PM</system>\nCONTEXTO:\n{evidencia_filtrada}\nTAREA: Evaluar {pregunta} bajo criterios {criterios}. Responder JSON."

    try:
        r = requests.post(LLAMA_API_URL, json={"prompt": prompt, "temperature": 0.0}, timeout=30)
        return jsonify({"resultado": r.json()['content']})
    except Exception as e:
        return jsonify({"error": f"Llama.cpp no responde: {str(e)}"}), 500

if __name__ == '__main__':
    # host 0.0.0.0 para acceso desde el celular
    app.run(host='0.0.0.0', port=5000, debug=False)
