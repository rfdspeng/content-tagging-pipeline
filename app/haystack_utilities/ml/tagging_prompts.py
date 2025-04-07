# V17
tagging_prompt = """
    I am doing a content tagging project. The goal of the project is to tag teaching materials.

    I will give you a text chunk, delimited in triple backticks, and you will identify all applicable tags based on the text chunk. You can only pick tags from this list: Data Analysis, Data Engineering, Data Science, Infrastructure and Operations, Machine Learning Engineering.

    Please format the tags as a Python list of strings. Respond only with the list, no other text, e.g. ["Machine Learning Engineering", "Data Science"].
    
    If none of the tags apply, respond with an empty list, [].

    Here are my guidelines for how to decide which tags to choose. I will give a topic followed by the recommended tags.
    * Anything related to processing data before modeling or analysis, e.g. collecting, ingesting, cleaning, normalizing, and moving data. This can include text preprocessing, image or video preprocessing, and any kind of data transformation. Examples of data collection include from databases, APIs, sensors, or via web scraping. Tag these as ["Data Engineering", "Data Science"].
    * Anything related to database design and data modeling: ["Data Engineering", "Data Science"].
    * Very simple data analysis like descriptive, diagnostic, and exploratory analysis, and data visualization: ["Data Analysis", "Data Science"].
    * Business intelligence and Excel tutorials: ["Data Analysis"].
    * Inferential data analysis: ["Data Science"].
    * Feature engineering: ["Data Science"].
    * Predictive and prescriptive data analysis: ["Data Science", "Machine Learning Engineering"].
    * Statistical modeling techniques like linear regression, logistic regression, decision trees, SVM, etc.: ["Data Science", "Machine Learning Engineering"].
    * Data labeling/annotation, both manual and with the help of LLMs: ["Data Science", "Machine Learning Engineering"].
    * Traditional NLP techniques like TF-IDF, BM25, bag-of-words: ["Data Science", "Machine Learning Engineering"].
    * Anything related to deep learning, including neural networks, modern computer vision, modern NLP, large language models, and AI: ["Data Science", "Machine Learning Engineering"].
    * Anything related to retrieval-augmented generation (RAG), like vector indexing and vector search: ["Data Science", "Machine Learning Engineering"].
    * Anything related to information retrieval and search engines: ["Data Science", "Machine Learning Engineering"].
    * Anything related to DevOps, including CI/CD, microservices, infrastructure as code (IaC), and application monitoring/logging. Anything related to deployment technologies, e.g. containerization, cloud services, and web application frameworks. Scalable computing infrastructure, e.g. distributed, parallel, and cloud computing. Tag these as ["Infrastructure and Operations"].
    * Anything related to MLOps, including distributed or cloud-based model training, model deployment, and post-deployment monitoring: ["Infrastructure and Operations", "Machine Learning Engineering"].

    Text chunk: ```{{doc.content}}```
    """

# V17 IPYNB
tagging_prompt_ipynb = """
    I am doing a content tagging project. The goal of the project is to tag teaching materials.

    I will give you a text chunk, delimited in triple backticks, and you will identify all applicable tags based on the text chunk. You can only pick tags from this list: Data Analysis, Data Engineering, Data Science, Infrastructure and Operations, Machine Learning Engineering.
    
    The text chunk is from a Jupyter Notebook that has been converted to Markdown.

    Please format the tags as a Python list of strings. Respond only with the list, no other text, e.g. ["Machine Learning Engineering", "Data Science"].
    
    If none of the tags apply, respond with an empty list, [].

    Here are my guidelines for how to decide which tags to choose. I will give a topic followed by the recommended tags.
    * Anything related to processing data before modeling or analysis, e.g. collecting, ingesting, cleaning, normalizing, and moving data. This can include text preprocessing, image or video preprocessing, and any kind of data transformation. Examples of data collection include from databases, APIs, sensors, or via web scraping. Tag these as ["Data Engineering", "Data Science"].
    * Anything related to database design and data modeling: ["Data Engineering", "Data Science"].
    * Very simple data analysis like descriptive, diagnostic, and exploratory analysis, and data visualization: ["Data Analysis", "Data Science"].
    * Business intelligence and Excel tutorials: ["Data Analysis"].
    * Inferential data analysis: ["Data Science"].
    * Feature engineering: ["Data Science"].
    * Predictive and prescriptive data analysis: ["Data Science", "Machine Learning Engineering"].
    * Statistical modeling techniques like linear regression, logistic regression, decision trees, SVM, etc.: ["Data Science", "Machine Learning Engineering"].
    * Data labeling/annotation, both manual and with the help of LLMs: ["Data Science", "Machine Learning Engineering"].
    * Traditional NLP techniques like TF-IDF, BM25, bag-of-words: ["Data Science", "Machine Learning Engineering"].
    * Anything related to deep learning, including neural networks, modern computer vision, modern NLP, large language models, and AI: ["Data Science", "Machine Learning Engineering"].
    * Anything related to retrieval-augmented generation (RAG), like vector indexing and vector search: ["Data Science", "Machine Learning Engineering"].
    * Anything related to information retrieval and search engines: ["Data Science", "Machine Learning Engineering"].
    * Anything related to DevOps, including CI/CD, microservices, infrastructure as code (IaC), and application monitoring/logging. Anything related to deployment technologies, e.g. containerization, cloud services, and web application frameworks. Scalable computing infrastructure, e.g. distributed, parallel, and cloud computing. Tag these as ["Infrastructure and Operations"].
    * Anything related to MLOps, including distributed or cloud-based model training, model deployment, and post-deployment monitoring: ["Infrastructure and Operations", "Machine Learning Engineering"].

    Text chunk: ```{{doc.content}}```
    """