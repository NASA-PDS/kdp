FROM kdp-node-validate:latest

# Add scripts
ADD ["validatedirectory", "/opt/local/kdp/validatedirectory"]
ADD ["scripts", "/opt/local/kdp/scripts"]

RUN chmod +x /opt/local/kdp/validatedirectory/validatedirectory.py /opt/local/kdp/scripts/get_products_from_label.sh