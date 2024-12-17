# Contributing to Sequent Microsystems Home Assistant Integrations

Thank you for your interest in contributing to Sequent Microsystems Home Assistant integrations! Since these integrations share a similar structure, improvements to one can often benefit others. To simplify the process, we’ve provided a helper script: `ha_project.sh`.  

## Getting Started with `ha_project.sh`

### Creating a New Integration
To create a new integration, you only need to modify `data.py`. The helper script will autogenerate the required code. Run the following command:  
```bash
./ha_project.sh data.py
```

### Updating an Existing Integration
If you're fixing bugs or adding features to an existing integration, you can use the script as well. Simply run:  
```bash
./ha_project.sh SMproject-ha
```
Here, `SMproject-ha` refers to the folder of the project repository you want to update.

## Editing Template Files
You may edit files inside `custom_components/SMtemplate*.py`, but keep in mind that these files should remain generic to support all integrations effectively.  

### Template Markers 
Should be avoided whenever possible.

While most of the code generation is automated, some parts require manual customization. These are marked with `__TEMPLATE__` macros for clarity. Below is a guide to these markers:

#### `README.md` Markers:
- `__TEMPLATE__`: Replaced with `FULL_NAME` from `data.py` (the full name of the card).  
- `__TEMPLATE_LINK__`: Replaced with `LINK` from `data.py` (link to the specific card on SequentMicrosystems.com).  
- `__TEMPLATE_README_ENTITIES__`: Automatically generates entities from `data.py`.  
- `__CUSTOM_README__ START` / `__CUSTOM_README__ END`: Defines the boundaries of custom blocks in `README.md`.

#### Entity Markers:
- `__CUSTOM_SETUP__ START` / `__CUSTOM_SETUP__ END`: Marks custom setup blocks for entities within `custom_components/SMtemplate`.
