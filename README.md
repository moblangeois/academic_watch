# Academic Watch

Academic Watch est une application qui surveille les publications académiques récentes sur des sujets spécifiques, résume les articles et envoie un digest quotidien par email.

## Fonctionnalités

- Surveillance des publications académiques récentes via l'API Clarivate.
- Résumé des articles utilisant les modèles OpenAI ou Ollama.
- Envoi d'un digest quotidien par email avec les résumés des articles.

## Configuration

Le fichier de configuration `config.ini` doit être placé dans le répertoire `config`. Voici un exemple de configuration :

```ini
[API]
clarivate_key = votre_clarivate_key
openai_key = votre_openai_key

[LLM]
provider = openai  # ou 'ollama'
openai_model = gpt-4o-mini
ollama_model = phi3.5

[EMAIL]
smtp_server = smtp.gmail.com
smtp_port = 587
sender_email = votre-email@gmail.com
sender_password = votre-mot-de-passe
recipient_email = destinataire-email@gmail.com

[SEARCH]
topics = ["Dynamic Capabilities"]
days_lookback = 1

[SYSTEM]
temp_dir = temp
log_dir = logs
```

## Installation

1. Cloner le dépôt :
    ```bash
    git clone https://github.com/votre-utilisateur/academic_watch.git
    cd academic_watch
    ```

2. Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

3. Configurer les clés API et les informations d'email dans le fichier `config.ini`.

## Utilisation

Pour exécuter l'application, utilisez la commande suivante :
```bash
python src/main.py
```

L'application est configurée pour s'exécuter quotidiennement à 08:00 et envoyer un digest par email. Vous pouvez modifier l'heure de l'exécution dans la fonction `main()` du fichier `src/main.py`.

## Dépendances

- openai
- ollama
- pydantic
- python-dotenv
- schedule
- requests
- clarivate/wosstarter_python_client

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des modifications que vous souhaitez apporter.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.