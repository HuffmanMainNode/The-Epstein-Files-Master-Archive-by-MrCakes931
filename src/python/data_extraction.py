import re
import json
import spacy

# Load the spaCy language model once
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # This part should ideally be handled outside the script for initial setup
    # In a Colab environment, it would typically be installed in a prior cell.
    print("spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
    nlp = None # Set to None to avoid errors if model is not present

def get_node_id(text, entity_type):
    """Generates a unique ID for a node based on its text and type."""
    # Simple sanitization for ID generation
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower() + '_' + entity_type.lower()

def extract_info_from_text(text_content, source_ref="Unknown Source"):
    """
    Extracts relevant information (nodes and edges) from raw text content using spaCy for NER and rule-based RE.

    Args:
        text_content (str): The raw text from which to extract information.
        source_ref (str): Reference to the source document or text.

    Returns:
        dict: A dictionary containing 'nodes' and 'edges' lists.
    """
    if nlp is None: # Handle case where spaCy model failed to load
        print("spaCy model not loaded, skipping extraction.")
        return {'nodes': [], 'edges': []}

    extracted_nodes = []
    extracted_edges = []
    node_ids = set() # To keep track of existing node IDs and avoid duplicates

    doc = nlp(text_content)

    # --- NER: Entity Extraction Logic ---
    # Using spaCy's pre-trained NER for general entities
    for ent in doc.ents:
        node_type = None
        label = ent.text.strip()
        node_id = None

        if ent.label_ == "PERSON":
            node_type = "Person"
            node_id = get_node_id(label, node_type)
        elif ent.label_ == "ORG":
            node_type = "Organization"
            node_id = get_node_id(label, node_type)
        elif ent.label_ == "GPE" or ent.label_ == "LOC": # Geo-Political Entity or Location
            node_type = "Location"
            node_id = get_node_id(label, node_type)
        elif ent.label_ == "EVENT":
            node_type = "Event"
            node_id = get_node_id(label, node_type)

        # Custom NER for Aircraft (using regex)
        if not node_type:
            aircraft_match = re.search(r'N\d{1,5}[A-Z]{1,2}', label) # e.g., N908JE
            if aircraft_match:
                node_type = "Aircraft"
                label = aircraft_match.group(0) # Use the matched part as label
                node_id = get_node_id(label, node_type)

        # Further custom types (e.g., specific objects if needed)

        if node_type and node_id and node_id not in node_ids:
            extracted_nodes.append({
                'id': node_id,
                'label': label,
                'type': node_type,
                'attributes': {'source_text_snippet': label, 'source_ref': source_ref}
            })
            node_ids.add(node_id)

    # Add generic 'JeffreyEpstein' node for relationship anchoring if not found by NER
    if 'jeffreyepstein_person' not in node_ids:
        extracted_nodes.append({
            'id': 'jeffreyepstein_person',
            'label': 'Jeffrey Epstein',
            'type': 'Person',
            'attributes': {'source_ref': source_ref}
        })
        node_ids.add('jeffreyepstein_person')

    # --- RE: Relation Extraction Logic (Rule-based and Dependency Parsing hints) ---
    for sent in doc.sents:
        # Convert sentence entities to a dict for easier lookup
        sent_entities = {get_node_id(ent.text.strip(), ent.label_): ent for ent in sent.ents}

        # Rule 1: 'employed by' (Person -> Organization)
        if re.search(r'\b(employed by|works for)\b', sent.text, re.IGNORECASE):
            for e1 in sent.ents:
                if e1.label_ == "PERSON":
                    for e2 in sent.ents:
                        if e2.label_ == "ORG":
                            # Simple check: is 'employed by' between them?
                            if e1.start < e2.start and "employed by" in sent.text[e1.end:e2.start].lower():
                                extracted_edges.append({
                                    'source': get_node_id(e1.text, "Person"),
                                    'target': get_node_id(e2.text, "Organization"),
                                    'type': 'employed_by',
                                    'attributes': {'sentence': sent.text, 'source_ref': source_ref}
                                })
                            elif e2.start < e1.start and "works for" in sent.text[e2.end:e1.start].lower(): # 'Org works for Person' is unlikely but for example
                                extracted_edges.append({
                                    'source': get_node_id(e1.text, "Person"),
                                    'target': get_node_id(e2.text, "Organization"),
                                    'type': 'employed_by',
                                    'attributes': {'sentence': sent.text, 'source_ref': source_ref}
                                })

        # Rule 2: 'associated with' (Person <-> Person/Organization)
        if re.search(r'\b(associated with|close to|friend of)\b', sent.text, re.IGNORECASE):
            persons = [e for e in sent.ents if e.label_ == "PERSON"]
            orgs = [e for e in sent.ents if e.label_ == "ORG"]

            if len(persons) >= 2:
                # Connect first two persons if 'associated with' is between them
                if "associated with" in sent.text[persons[0].end:persons[1].start].lower():
                    extracted_edges.append({
                        'source': get_node_id(persons[0].text, "Person"),
                        'target': get_node_id(persons[1].text, "Person"),
                        'type': 'associated_with',
                        'attributes': {'sentence': sent.text, 'source_ref': source_ref}
                    })
            if persons and orgs:
                # Connect a person to an organization
                for p in persons:
                    for o in orgs:
                        if "associated with" in sent.text[min(p.end, o.end):max(p.start, o.start)].lower():
                             extracted_edges.append({
                                'source': get_node_id(p.text, "Person"),
                                'target': get_node_id(o.text, "Organization"),
                                'type': 'associated_with',
                                'attributes': {'sentence': sent.text, 'source_ref': source_ref}
                            })

        # Rule 3: 'travelled to' (Person/Aircraft -> Location)
        travel_keywords = r'\b(travelled to|flew to|visited)\b'
        if re.search(travel_keywords, sent.text, re.IGNORECASE):
            locations = [e for e in sent.ents if e.label_ in ("GPE", "LOC")]
            persons_or_aircraft = [e for e in sent.ents if e.label_ == "PERSON" or re.search(r'N\d{1,5}[A-Z]{1,2}', e.text)]

            for subj in persons_or_aircraft:
                for loc in locations:
                    if subj.start < loc.start and re.search(travel_keywords, sent.text[subj.end:loc.start], re.IGNORECASE):
                        subj_type = "Person" if subj.label_ == "PERSON" else "Aircraft"
                        extracted_edges.append({
                            'source': get_node_id(subj.text, subj_type),
                            'target': get_node_id(loc.text, "Location"),
                            'type': 'travelled_to',
                            'attributes': {'sentence': sent.text, 'source_ref': source_ref}
                        })

        # Rule 4: 'owned by' (Location/Aircraft/Organization -> Person/Organization)
        owned_keywords = r'\b(owned by|belonged to)\b'
        if re.search(owned_keywords, sent.text, re.IGNORECASE):
            owners = [e for e in sent.ents if e.label_ in ("PERSON", "ORG")]
            owned_items = [e for e in sent.ents if e.label_ in ("GPE", "LOC") or re.search(r'N\d{1,5}[A-Z]{1,2}', e.text) or e.label_ == "ORG"]

            for item in owned_items:
                for owner in owners:
                    if item.start < owner.start and re.search(owned_keywords, sent.text[item.end:owner.start], re.IGNORECASE):
                        item_type = None
                        if item.label_ in ("GPE", "LOC"): item_type = "Location"
                        elif re.search(r'N\d{1,5}[A-Z]{1,2}', item.text): item_type = "Aircraft"
                        elif item.label_ == "ORG": item_type = "Organization"

                        if item_type:
                            owner_type = "Person" if owner.label_ == "PERSON" else "Organization"
                            extracted_edges.append({
                                'source': get_node_id(item.text, item_type),
                                'target': get_node_id(owner.text, owner_type),
                                'type': 'owned_by',
                                'attributes': {'sentence': sent.text, 'source_ref': source_ref}
                            })

        # Rule 5: 'attended' (Person -> Event)
        attended_keywords = r'\b(attended|was at)\b'
        if re.search(attended_keywords, sent.text, re.IGNORECASE):
            persons = [e for e in sent.ents if e.label_ == "PERSON"]
            events = [e for e in sent.ents if e.label_ == "EVENT"]

            for p in persons:
                for ev in events:
                    if p.start < ev.start and re.search(attended_keywords, sent.text[p.end:ev.start], re.IGNORECASE):
                        extracted_edges.append({
                            'source': get_node_id(p.text, "Person"),
                            'target': get_node_id(ev.text, "Event"),
                            'type': 'attended',
                            'attributes': {'sentence': sent.text, 'source_ref': source_ref}
                        })

    # Deduplicate nodes and edges based on a combination of fields if necessary
    # For this exercise, we assume adding nodes checks by ID, and edges are just appended.

    return {
        'nodes': extracted_nodes,
        'edges': extracted_edges
    }

if __name__ == '__main__':
    # Example usage for testing
    test_texts = [
        "Jeffrey Epstein was associated with Ghislaine Maxwell. He owned an aircraft N123AB and travelled to Little St. James.",
        "Pilot A was employed by JE Enterprise. David Copperfield attended a party in London.",
        "The aircraft N908JE belonged to Jeffrey Epstein."
    ]

    all_extracted_nodes = []
    all_extracted_edges = []
    existing_node_ids = set()

    for i, sample_text in enumerate(test_texts):
        print("
Processing text {}: {}".format(i+1, sample_text))
        extracted_data = extract_info_from_text(sample_text, source_ref="Sample_Text_{}".format(i+1))

        # Add unique nodes
        for node in extracted_data['nodes']:
            if node['id'] not in existing_node_ids:
                all_extracted_nodes.append(node)
                existing_node_ids.add(node['id'])

        # Add all edges (deduplication for edges would be more complex, e.g. (source, target, type) combo)
        all_extracted_edges.extend(extracted_data['edges'])

    print("
--- Final Extracted Data ---")
    print("Nodes:")
    print(json.dumps(all_extracted_nodes, indent=4))
    print("
Edges:")
    print(json.dumps(all_extracted_edges, indent=4))
