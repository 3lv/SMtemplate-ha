#!/usr/bin/bash

# Ask for project details
read -p "Enter project name (e.g., SMioplus): " project_name

# Define directories
template_dir="/home/vlad/workspace/sequent/ha/SMtemplate-ha"
template_cdir="${template_dir}/custom_components/SMtemplate"
project_dir="${project_name}-ha"
project_cdir="${project_dir}/custom_components/${project_name}"

cp_update_file() {
	local source_file="$1"
	local target_file="$2"
	#cp -f "$target_file" "${target_file}.bak"
	local section=$(sed -n '/### CUSTOM_SETUP START/,/### CUSTOM_SETUP END/p' "$source_file")
	cp -f "$source_file" "$target_file"
	sed -i "/### CUSTOM_SETUP START/,/### CUSTOM_SETUP END/c\\
	$section" "$target_file"
}

if [ -d "${project_dir}" ]; then
	read -p "Project already exists, updating? (y/n): " choice
	if [[ "$choice" != "y" ]]; then
		echo "Canceled\n"
		exit 1
	fi
	project_cdir=$(find "${project_dir}/custom_components" -mindepth 1 -maxdepth 1 -type d)
	files=($(find "${project_cdir}" -type f -name "*.py" ! -name "data.py" | sort))
	for file in "${files[@]}"; do
	    filename=$(basename -- "$file")
	    read -p "Do you want to update ${filename}? (y/n): " choice
	    if [[ "$choice" == "y" ]]; then
		cp_update_file "${template_cdir}/${filename}" "${project_cdir}/${filename}"
		#cp -f "${template_cdir}/${filename}" "${project_cdir}/${filename}"
	    fi
	done
	read -p "Create commit and fast upload? (y/n): " choice
	if [[ "$choice" != "y" ]]; then
		echo "Canceled\n"
		exit 0
	fi
	cd "${project_dir}"
	git add -A
	git commit -m "Updated from template (using script)"
	git push origin master
else
	mkdir -p "${project_cdir}"
	read -p "Enter full project name (e.g., Home Automation): " full_project_name
	read -p "Enter project link (e.g., https://s../products/name): " project_link

	sed_cmd="s#__TEMPLATE__#${full_project_name}#g; s|__TEMPLATE_LINK__|${project_link}|g; s#SMtemplate#${project_name}#g"
	sed "${sed_cmd}" "${template_dir}/hacs.json" > "${project_dir}/hacs.json"
	sed "${sed_cmd}" "${template_dir}/README.md" > "${project_dir}/README.md"
	sed "${sed_cmd}" "${template_cdir}/manifest.json" > "${project_cdir}/manifest.json"
	cp "${template_cdir}/__init__.py" "${project_cdir}/"
	files=($(find "${template_cdir}" -type f -name "*.py" ! -name "__init__.py" | sort))
	for file in "${files[@]}"; do
	    filename=$(basename -- "$file")
	    read -p "Do you want to copy ${filename}? (y/n): " choice
	    if [[ "$choice" == "y" ]]; then
		cp "$file" "${project_cdir}/"
	    fi
	done

	cd "${project_dir}"
	git init >/dev/null 2>&1
	echo "New project ${project_name}-ha created successfully!"
	echo "data.py must be changed acordingly!"
fi
