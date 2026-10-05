import json

new_roadmap = {
  "id": "machine-learning",
  "title": "Machine Learning & AI",
  "description": "Learn ML fundamentals, deep learning, and AI engineering",
  "icon": "brain",
  "color": "#9b59b6",
  "sections": [
    {
      "id": "data-science-basics",
      "title": "Data Science Fundamentals",
      "nodes": [
        {
          "id": "numpy",
          "title": "NumPy",
          "status": "todo",
          "description": "N-dimensional arrays, matrix operations, and numerical computing in Python.",
          "resources": ["NumPy Documentation"]
        },
        {
          "id": "pandas",
          "title": "Pandas",
          "status": "todo",
          "description": "Data manipulation, cleaning, and analysis using DataFrames.",
          "resources": ["Pandas Guide"]
        },
        {
          "id": "matplotlib",
          "title": "Data Visualization",
          "status": "todo",
          "description": "Plotting charts and visualizing data distributions using Matplotlib and Seaborn.",
          "resources": []
        }
      ]
    },
    {
      "id": "ml-basics",
      "title": "Machine Learning Basics",
      "nodes": [
        {
          "id": "supervised-learning",
          "title": "Supervised Learning",
          "status": "todo",
          "description": "Linear regression, logistic regression, decision trees, and random forests.",
          "resources": ["Scikit-Learn Docs"]
        },
        {
          "id": "unsupervised-learning",
          "title": "Unsupervised Learning",
          "status": "todo",
          "description": "Clustering (K-Means), dimensionality reduction (PCA), and anomaly detection.",
          "resources": []
        },
        {
          "id": "model-evaluation",
          "title": "Model Evaluation",
          "status": "todo",
          "description": "Cross-validation, precision, recall, F1-score, ROC curves, and overfitting/underfitting.",
          "resources": []
        }
      ]
    },
    {
      "id": "deep-learning",
      "title": "Deep Learning",
      "nodes": [
        {
          "id": "neural-networks",
          "title": "Neural Networks",
          "status": "todo",
          "description": "Perceptrons, activation functions, backpropagation, and loss functions.",
          "resources": ["3Blue1Brown Neural Networks"]
        },
        {
          "id": "pytorch-tf",
          "title": "PyTorch & TensorFlow",
          "status": "todo",
          "description": "Building and training neural networks using modern deep learning frameworks.",
          "resources": []
        },
        {
          "id": "cnn-rnn",
          "title": "CNNs & RNNs",
          "status": "todo",
          "description": "Convolutional Neural Networks for images, Recurrent Neural Networks for sequential data.",
          "resources": []
        }
      ]
    },
    {
      "id": "generative-ai",
      "title": "Generative AI & LLMs",
      "nodes": [
        {
          "id": "transformers",
          "title": "Transformers",
          "status": "todo",
          "description": "Self-attention mechanism, BERT, GPT architecture, and huggingface ecosystem.",
          "resources": ["Attention Is All You Need"]
        },
        {
          "id": "prompt-engineering",
          "title": "Prompt Engineering",
          "status": "todo",
          "description": "Designing effective prompts, zero-shot/few-shot learning, and context window optimization.",
          "resources": []
        },
        {
          "id": "rag",
          "title": "RAG & Agents",
          "status": "todo",
          "description": "Retrieval-Augmented Generation, vector databases, LangChain, and AI agents.",
          "resources": []
        }
      ]
    }
  ]
}

with open('data/learning/roadmaps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Ensure 'roadmaps' list exists
if 'roadmaps' not in data:
    data['roadmaps'] = []

# Remove existing machine-learning roadmap if it exists to avoid duplicates
data['roadmaps'] = [rm for rm in data['roadmaps'] if rm.get('id') != 'machine-learning']

data['roadmaps'].append(new_roadmap)

with open('data/learning/roadmaps.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Added Machine Learning roadmap to roadmaps.json")
