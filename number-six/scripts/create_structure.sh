#!/bin/bash

# Create directory structure for all 32 domains

DOMAINS=(
    "01_cloud_computing"
    "02_software_engineering"
    "03_data_science_ai"
    "04_cybersecurity"
    "05_devops_sre"
    "06_mobile_development"
    "07_game_development"
    "08_blockchain_web3"
    "09_iot_embedded"
    "10_product_management"
    "11_ux_ui_design"
    "12_digital_marketing"
    "13_sales_engineering"
    "14_technical_writing"
    "15_quality_assurance"
    "16_database_engineering"
    "17_network_engineering"
    "18_systems_architecture"
    "19_business_intelligence"
    "20_project_management"
    "21_financial_technology"
    "22_healthcare_technology"
    "23_education_technology"
    "24_legal_technology"
    "25_manufacturing_industry_4_0"
    "26_telecommunications"
    "27_media_entertainment_tech"
    "28_energy_sustainability_tech"
    "29_agriculture_technology"
    "30_transportation_logistics"
    "31_real_estate_technology"
    "32_research_development"
)

# Create each domain structure
for domain in "${DOMAINS[@]}"; do
    echo "Creating structure for $domain..."

    # Create domain directories
    mkdir -p "$domain/standards/"{style-guides,api-guides,legacy-integration-guides,evidence,patterns}
    mkdir -p "$domain/skills"

    # Create 10 subskills for each domain
    for i in $(seq -f "%02g" 1 10); do
        mkdir -p "$domain/skills/${i}_subskill/"{reference,guides,src}
    done
done

echo "Directory structure created successfully!"
