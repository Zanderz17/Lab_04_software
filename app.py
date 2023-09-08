import boto3
import csv
import json
import requests

def lambda_handler(event, context):
    # Initialize the S3 client
    s3 = boto3.client('s3')

    # Specify your S3 bucket and file name
    bucket_name = 'class-demo-bgc'
    file_name = 'pokefile.csv'

    try:
        # Read the CSV file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        content = response['Body'].read().decode('utf-8')

        # Initialize a list to store Pokémon data
        pokemon_data = []

        # Parse the CSV content, skipping the first row (header)
        csv_reader = csv.reader(content.splitlines())
        header = next(csv_reader)  # Skip the first row (header)
        for row in csv_reader:
            # Assuming the CSV has columns: Nombre, Peso, Altura, Tipo
            nombre, peso, altura, tipo = row

            # Make an API request to get additional Pokémon information
            pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{nombre.lower()}/'
            response = requests.get(pokemon_url)
            if response.status_code == 200:
                pokemon_info = response.json()

                # Extract abilities and forms data
                abilities = [ability['ability']['name'] for ability in pokemon_info['abilities']]
                forms = [form['name'] for form in pokemon_info['forms']]

                # Create a dictionary for each Pokémon with additional information
                pokemon = {
                    'Nombre': nombre,
                    'Peso': peso,
                    'Altura': altura,
                    'Tipo': tipo,
                    'Habilidades': abilities,
                    'Formas': forms,
                    'Imagen': pokemon_info['sprites']['front_default']
                }

                # Append the Pokémon data to the list
                pokemon_data.append(pokemon)

        # Print the Pokémon data to the Lambda logs
        for pokemon in pokemon_data:
            print(json.dumps(pokemon, indent=4))

        # Return the Pokémon data as a JSON response
        return {
            'statusCode': 200,
            'body': json.dumps(pokemon_data, indent=4)  # Format with indentation
        }
    except Exception as e:
        print(f'Error: {e}')
        return {
            'statusCode': 500,
            'body': 'Error reading CSV file from S3.'
        }