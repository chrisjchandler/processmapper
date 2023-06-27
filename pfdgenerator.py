from flask import Flask, render_template, request
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import networkx as nx

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_pfd', methods=['POST'])
def generate_pfd():
    workflows = request.form.getlist('workflow[]')

    # Validate the workflows
    if not validate_workflows(workflows):
        return 'Invalid workflow data'

    parsed_workflows = parse_workflows(workflows)

    # Generate PFD diagram
    G = generate_pfd_diagram(parsed_workflows)

    # Convert diagram image to base64
    image_base64 = generate_base64_image(G)

    return image_base64

def validate_workflows(workflows):
    if len(workflows) % 5 != 0:
        return False

    for i in range(0, len(workflows), 5):
        process_name = workflows[i].strip()
        entity1_name = workflows[i+1].strip()
        entity1_type = workflows[i+2].strip()
        entity2_name = workflows[i+3].strip()
        entity2_type = workflows[i+4].strip()

        if not process_name or not entity1_name or not entity1_type or not entity2_name or not entity2_type:
            return False

        if not validate_entity_name(entity1_name) or not validate_entity_name(entity2_name):
            return False

    return True

def parse_workflows(workflows):
    parsed_workflows = []
    for i in range(0, len(workflows), 5):
        process_name = workflows[i].strip()
        entity1_name = workflows[i+1].strip()
        entity1_type = workflows[i+2].strip()
        entity2_name = workflows[i+3].strip()
        entity2_type = workflows[i+4].strip()

        parsed_workflow = {
            'process_name': process_name,
            'data_entities': [
                {'name': entity1_name, 'type': entity1_type},
                {'name': entity2_name, 'type': entity2_type}
            ]
        }

        parsed_workflows.append(parsed_workflow)

    return parsed_workflows

def validate_entity_name(name):
    # Add your validation logic here
    return True

def generate_pfd_diagram(workflows):
    G = nx.DiGraph()

    for workflow in workflows:
        process_name = workflow['process_name']
        data_entities = workflow['data_entities']

        # Add process node
        G.add_node(process_name, shape='rectangle')

        for entity in data_entities:
            entity_name = entity['name']
            entity_type = entity['type']

            # Add entity node
            G.add_node(entity_name, shape='ellipse')

            # Add edge from entity to process
            G.add_edge(entity_name, process_name, label=entity_type)

    return G

def generate_base64_image(G):
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx(G, pos, with_labels=True, node_color='lightblue', font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.axis('off')

    # Save diagram to BytesIO
    image_buffer = BytesIO()
    plt.savefig(image_buffer, format='png')
    plt.close()

    # Convert diagram image to base64
    image_base64 = base64.b64encode(image_buffer.getvalue()).decode('utf-8')

    return image_base64

if __name__ == '__main__':
    app.run()
