#!/usr/bin/bash

KEEP_MARKERS=("CUSTOM_SETUP" "__CUSTOM_README__")

data_py=${1:?Must provide data.py path}
data_py=$(find "$data_py" -type f -name data.py)

project_name=$(grep -E 'DOMAIN *= *"' "$data_py" | sed -E 's/.*DOMAIN *= *"(.*)"/\1/')
[ -z "$project_name" ] && { echo "Error: DOMAIN variable not found in $data_py"; exit 1; }

project_full_name=$(grep -E 'FULL_NAME *= *"' "$data_py" | sed -E 's/.*FULL_NAME *= *"(.*)"/\1/')
[ -z "$project_full_name" ] && { echo "Error: FULL_NAME variable not found in $data_py"; exit 1; }

project_link=$(grep -E 'LINK *= *"' "$data_py" | sed -E 's/.*LINK *= *"(.*)"/\1/')
[ -z "$project_link" ] && { echo "Error: LINK variable not found in $data_py"; exit 1; }

#read -rp "Enter full project name (e.g., Home Automation): " project_full_name
#read -rp "Enter project link (e.g., https://s../products/name): " project_link

# Run the Python script and capture its output as JSON
json_output=$(python3 /home/vlad/bin/parse_data.py "${data_py}")

# Check if jq is installed
if ! command -v jq &> /dev/null; then
	echo "jq is not installed. Please install jq."
	exit 1
fi

# Parse the JSON output to get the types
entity_types=($(echo "$json_output" | jq -r 'keys[]'))

# Loop through each type
readme_entities_arr=()
for type in "${entity_types[@]}"; do
    entities=$(echo "$json_output" | jq -r --arg type "$type" '.[$type] | keys[]')
    for entity in $entities; do
	    chan_no=$(echo "$json_output" | jq -r --arg type "$type" --arg entity "$entity" '.[$type][$entity]')
	    if [[ $chan_no == 1 ]]; then
		    readme_entities_arr+=("${entity}_1: (type: ${type})")
	    else
		    readme_entities_arr+=("${entity}_1: -> ${entity}_${chan_no}:  (type: ${type})")
	    fi
    done
done
printf -v readme_entities "%s\n" "${readme_entities_arr[@]}"
readme_entities=${readme_entities%?}

#echo "${readme_entities}" # DEBUG

# Define directories
template_dir="/home/vlad/workspace/sequent/ha/SMtemplate-ha"
template_cdir="${template_dir}/custom_components/SMtemplate"
project_dir="${project_name}-ha"
project_cdir="${project_dir}/custom_components/${project_name}"
origin_url="https://github.com/SequentMicrosystems/${project_dir}"

escape() {
	echo "$1" | sed ':a;N;$!ba;s/\n/\\n/g' | sed 's/\$/\\$/g'
}

replace_in_file() {
	file="$1"
	ORIGINALSTRING="$2" REPLACEMENTSTRING="$3" awk '
		BEGIN {
			old = ENVIRON["ORIGINALSTRING"]
			new = ENVIRON["REPLACEMENTSTRING"]
		}
		s = index($0,old) {
			$0 = substr($0,1,s-1) new substr($0,s+length(old))
		}
		{ print }
	' file
}

cp_update_file() {
	local source_file="$1"
	local target_file="$2"
	local new_file=false
	if [[ ! -f "$2" ]]; then
		new_file=true
	fi
	local temp_file="$2.temp"
	sed_cmd="s#__TEMPLATE__#${project_full_name}#g; s|__TEMPLATE_LINK__|${project_link}|g; s#SMtemplate#${project_name}#g; s#__TEMPLATE_README_ENTITIES__#$(escape "$readme_entities")#g"
	sed "${sed_cmd}" "${source_file}" > "${temp_file}"
	sed -i "s/ (replace SMioplus-ha with SMioplus-ha)//" "${temp_file}"
	if [[ $new_file = false ]]; then
		for marker in "${KEEP_MARKERS[@]}"; do
			local section
			section=$(sed -n "/${marker} START/,/${marker} END/p" "$target_file")
			if [[ -z $section ]]; then
				continue
			fi
			escaped_section=$(escape "$section")
			sed -i "/${marker} START/,/${marker} END/c\\
$escaped_section" "$temp_file"
		done
	fi
	if diff "$temp_file" "$target_file" > /dev/null; then
		rm "${temp_file}"
		return
	fi
	cp -f "$temp_file" "$target_file"
	rm "${temp_file}"
	if [[ $new_file = false ]]; then
		echo "Updated $(basename -- "$target_file")"
	else
		echo "Created $(basename -- "$target_file")"
	fi
}

if [ -d "${project_dir}" ]; then
	read -rp "Project already exists, updating? (y/n): " choice
	if [[ "$choice" != "y" ]]; then
		echo "Canceled"
		exit 1
	fi
else
	new_project=true
	read -rp "Project doesn't exist, create now? (y/n): " choice
	if [[ "$choice" != "y" ]]; then
		echo "Canceled"
		exit 1
	fi
	mkdir -p "${project_cdir}"
fi
#project_cdir=$(find "${project_dir}/custom_components" -mindepth 1 -maxdepth 1 -type d)
#project_cdir="${project_dir}/custom_components/${project_name}"
cfiles=()
if [[ "$data_py" != "${project_cdir}/data.py" ]]; then
	cp -f "$data_py" "${project_cdir}/data.py"
fi
for type in "${entity_types[@]}"; do
	cfiles+=("${type}.py")
done
cfiles+=("manifest.json" "__init__.py")
for file in "${cfiles[@]}"; do
	filename=$(basename -- "$file")
	cp_update_file "${template_cdir}/${filename}" "${project_cdir}/${filename}"
done
files=("hacs.json" "README.md")
for filename in "${files[@]}"; do
	cp_update_file "${template_dir}/${filename}" "${project_dir}/${filename}"
done
cd "${project_dir}" || exit
if [[ $new_project = true ]]; then
	git init 2>/dev/null
	git remote add origin "$origin_url"
fi
diff_output=$(git diff --stat)
if [[ -z $diff_output ]]; then
	echo "  No changes"
else
	git diff --stat
fi
read -rp "Create commit and fast upload? (y/n): " choice
if [[ "$choice" != "y" ]]; then
	echo "Canceled"
	exit 0
fi
git add -A
git commit -m "Updated from template (using script)"
git push origin master
