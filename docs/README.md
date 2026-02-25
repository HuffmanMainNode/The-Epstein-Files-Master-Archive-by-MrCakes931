# The Epstein Files Master Archive by MrCakes931

## Project Overview

This repository serves as a comprehensive digital archive and forensic mapping project dedicated to uncovering and visualizing the intricate network surrounding the Jeffrey Epstein enterprise. Our goal is to consolidate disparate pieces of information, entities, and relationships into a structured, searchable, and analyzable format.

## Goals

The primary objectives of this project are:

*   **Forensic Mapping**: To systematically identify, categorize, and establish connections between individuals, organizations, locations, aircrafts, financial transactions, and events related to Jeffrey Epstein and his associates.
*   **Data Consolidation**: To act as a central repository for publicly available information, court documents, investigative reports, and other relevant data points.
*   **Transparency and Accessibility**: To provide a clear, understandable, and accessible visualization of the network, aiding researchers, journalists, and the public in comprehending the scale and complexity of the enterprise.
*   **Pattern Identification**: To leverage data visualization and analysis techniques to identify hidden patterns, clusters, and unusual activities within the network.

## Repository Organization

This repository is structured to facilitate systematic data collection, processing, analysis, and archiving. Below is an overview of the key directories:

*   `archive/`: Contains raw source materials, such as original documents, news articles, and links, to ensure traceability and verifiability of all extracted information.
    *   `archive/documents/`: Stores actual copies or summaries of source documents.
*   `data/` (Proposed future directory for structured datasets):
    *   `data/raw_data/`: Stores raw, unprocessed data collected from various sources.
    *   `data/processed_data/`: Stores cleaned, transformed, and ready-for-analysis datasets.
*   `src/` (Proposed future directory for modular code):
    *   `src/data_extraction.py`: Contains the core logic for extracting entities and relationships from text (Named Entity Recognition - NER) and inferring connections (Relation Extraction - RE). This script uses `spaCy` for advanced NLP capabilities.
    *   `src/utils.py`: (Proposed) Utility functions for data manipulation, cleaning, etc.
*   `models/`: (Proposed) Stores any machine learning models developed for advanced analysis or prediction.
*   `notebooks/`: (Proposed) Contains Jupyter notebooks for exploratory data analysis, visualization, and ad-hoc scripting.
*   `visualizations/`: (Proposed) Stores generated visualizations of the topology map and other data insights.
*   `docs/`: (Proposed) Additional documentation, research notes, and methodologies.

## Key Files

*   `README.md`: This document, serving as the project's 'library card'.
*   `master_topology.json`: The core network graph, storing nodes (entities) and edges (relationships) of the Epstein network.
*   `full_database.json`: A comprehensive database of all extracted and standardized records, including nodes, edges, and document references, acting as the structured backend for the topology map.
*   `VERSION.txt`: Tracks the project's current version number (e.g., `1.a.2`).
*   `data_extraction.py`: The Python script responsible for programmatically extracting entities and relationships from textual data.

## File Naming Conventions

To maintain consistency and ease of navigation, the following conventions are adopted:

*   **Documents**: `source_description_YYY-MM-DD.ext` (e.g., `court_document_maxwell_2023-01-15.pdf`).
*   **Scripts**: `purpose_of_script.py` (e.g., `extract_entities.py`).
*   **Notebooks**: `yyyy-mm-dd_descriptive_title.ipynb` (e.g., `2023-01-15_eda_flight_data.ipynb`).
*   **JSON Data**: `entity_type.json` or `dataset_name.json` (e.g., `master_topology.json`, `full_database.json`).

## Versioning System

The project uses a `X.y.Z` versioning scheme, recorded in `VERSION.txt`:

*   **X (Major Release)**: Denotes significant architectural changes or milestones.
*   **y (Feature Release)**: Indicates new features, substantial data integrations, or major methodological updates.
*   **Z (Patch/Minor Update)**: Represents bug fixes, small data additions, minor enhancements to existing features, or documentation updates.

The versioning is automated: upon major updates or integrations, the script reads `VERSION.txt`, increments the `Z` component, and saves the new version back to the file before committing. This ensures transparent tracking of project evolution.

## How to Navigate and Contribute

1.  **Clone the Repository**: Start by cloning this repository to your local machine.
2.  **Understand the Structure**: Familiarize yourself with the `Repository Organization` section above to locate relevant files.
3.  **Explore the Topology**: Examine `master_topology.json` to understand the current state of the network graph. `full_database.json` provides the granular detail and source traceability for each node and edge.
4.  **Data Extraction**: Contributions to data extraction typically involve enhancing `data_extraction.py` or running it on new source materials.
5.  **Adding New Data**: After extracting new data, integrate it into `full_database.json` and subsequently update `master_topology.json`. Ensure `VERSION.txt` is appropriately incremented.
6.  **Archiving Sources**: Always archive new source materials in `archive/documents/` and link them in `full_database.json`.
7.  **Commit and Push**: Regularly commit your changes with descriptive messages (e.g., `feat: [v1.a.2] Integrated new data sources`) and push them to the `main` branch. Use `git add .`, `git commit -m "Your message"`, and `git push origin main`.
8.  **Propose Changes**: For significant changes or new features, please open an issue or submit a pull request for review.

This 'library card' aims to guide all contributors and stakeholders in leveraging this archive effectively for the ongoing investigation into the Jeffrey Epstein enterprise.
