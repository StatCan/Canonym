Le français suit l'anglais

""""""""""""""""
Canonym - Anonymization Package 
""""""""""""""""

==========================
Installation 
==========================

Create a virtual environment with Python >=3.9 
.. code::

    conda create -n=canonym python=3.9
    conda activate canonym

You can install Canonym using the wheel located in the dist folder:

.. code::

    pip install dist\canonym_public-2023.9.15-py3-none-any.whl
    
    
=======================
Usage
=======================

---------------------
Basic usage
---------------------

.. code:: python

    from canonym import Canonym
    
    anonymizer = Canonym()
    
    text = "This is John Doe, from Ottawa, his phone numer is 123-456-7890"
    anonymizer.anonymize(text)
    
    
Canonym can accept as an input the following :
    - string
    - list of strings
    - Textitem object
    - Pandas Series
    - Pandas DataFrame
    
You can use directly the **anonymize()** method, or use the input specific methods : 
    - **str**: anonymizer.anonymize_text,
    - **TextItem**: anonymizer.anonymize_text,
    - **list**: anonymizer.anonymize_list,
    - **DataFrame**: anonymizer.anonymize_dataframe,
    - **Series**: anonymizer.anonymize_pd_series
	
----------------------
Strategies
----------------------

The following default are available by default: 

- **replace_all_with_tag** :  replaces all entities with their Entity Type
- **redact_all** : redacts all PI 
- **hash_all** : Hashes the PI entities
- **mask_all** : Masks all DEFAULT  entities
- **scramble_all** : Scrambles (changes the order of letters) for all entities
- **mixed_per_entity_type** : {hash : ALPHABET_ENTITIES, mask : SPECIAL_ENTITIES, randomize : NUMERIC_ENTITIES, redact : ALPHANUMERIC_ENTITIES}
- **hash_one** : {hash: [PERSON]}
- **mask_some**: {mask: [PERSON, FULL_ADDRESS], redact: [PHONE_NUMBER]}
- **replace_custom**: {replace: CUSTOM_ENTITIES}
- **redact_custom**: {redact : CUSTOM_ENTITIES}
- **faker_custom**: {faker : CUSTOM_ENTITIES}
- **faker_all**: {faker : DEFAULT_ENTITIES}
- **replace_w_value_custom**: {replace_val : CUSTOM_ENTITIES}

	
By default the anonymize method will use the *replace_all_with_tag* strategy, to use a different strategy use :

.. code:: python
	
	anonymizer.anonymize(text, strategy='redact_all')

	
-----------------------
Language
-----------------------

The **language** parameter provides the language of the text, defaults to english, if *None* or "auto" are provided a search will be conducted
to automatically find the right language for each text input. By default Canonym handles English and French text.

In the case of a Pandas DataFrame, also accepts a dict of format **{column_name:language or auto, }**, 
so each collumn can be set to a different language or to automatic search. 

.. code:: python

    # a string
    anonymizer.anonymize(text, strategy='redact_all', language='fr')
    # a Pandas DataFrame
    anonymizer.anonymize(df, language={'column1': 'en', 'column2': 'fr', 'column3': 'auto'} )


------------------------
Advanced Configuration
------------------------

The behaviour of Canonym can be modified, by editing the two configuration files :
    - ner_config_default.yaml
    - anonymizer_config_default.yaml
    
in **ner_config_default.yaml** the following can be defined :

    - AVAILABLE_LANGS  : Which language Canonym can handle, defaults to *en* and *fr* 
    - SCORE_THRESHOLD  : The confidence score threshold over which an entity is tagged, defaults at **0.4**
    - DEFAULT_RECOGNIZERS  : List of recognizers loaded by Canonym 
    - POST_PROCESSING_ENTITIES  : Entity specific post-processing 
    - PRESIDIO_NLP_ENGINE_CONFIG  : Some entities will be handled by a spacy engine that needs to be defined
        -  nlp_engine_name
        -  models      
    - SPACY_ENTITIES  :  List of entities, that need to be handled by Spacy
    - TRANSFORMER_MODELS_ENTITIES  :  List of entities, that need to be handled by the Transformers models 
    - TRANSFORMER_MODELS_ENHANCERS :  Post processing enhancement for the Tags provided by the Transformers models  (Extending partial words or merging similar contiguous entities)

in **anonymizer_config_default.yaml** the following can be defined :

    - AVAILABLE_LANGS :  Which language Canonym can handle, defaults to *en* and *fr* 
    - DEFAULT_ENTITIES:  List of all entities that can be anonmymized
    - ALPHABET_ENTITIES: Set of Alphabet entities
    - SPECIAL_ENTITIES:  Set of special entities ( email, url, etc..)
    - NUMERIC_ENTITIES:
    - ALPHANUMERIC_ENTITIES:
    - CUSTOM_ENTITIES:  Custom set of entities to be redacted 
    - ALL_ANONYMIZER_STRATEGIES: List of strategies, a strategy is defined as :
             *strategy_name* : {anonymization_action_1 : SET_1_OF_ENTITES, anonymization_action_2 : SET_2_OF_ENTITES}


==========================
Contributing
==========================
Before contributing please read the instructions in CONTRIBUTING.md 

link: [CONTRIBUTING.MD](https://github.com/StatCan/Canonym/blob/main/CONTRIBUTING.md)

==========================
LICENSE
==========================
[MIT License](https://github.com/StatCan/Canonym/blob/main/LICENSE)

""""""""""""""""
Canonym - Librairie d'anonymisation 
Statistique Canada
""""""""""""""""

==========================
Installation
==========================

Créer un environnement virtuel avec Python >=3.9 
... code::

    conda create -n=canonym python=3.9
    conda activate canonym

Vous pouvez installer Canonym en utilisant le fichier whl situé dans le dossier dist :

... code::

    pip install dist\canonym_public-2023.9.15-py3-none-any.whl
    
    
=======================
Utilisation
=======================

---------------------
Utilisation de base
---------------------

... code:: python

    from canonym import Canonym
    
    anonymizer = Canonym()
    
    text = "This is John Doe, from Ottawa, his phone number is 123-456-7890"
    anonymizer.anonymize(text)
    
    
Canonym peut accepter comme intrants :
    - chaîne de caractères
    - liste de chaînes de caractères
    - objet Textitem
    - Série Pandas
    - DataFrame Pandas
    
Vous pouvez utiliser directement la méthode **anonymize()**, ou utiliser les méthodes spécifiques à chaque type d'intrants : 
    - **str** : anonymizer.anonymize_text,
    - **TextItem** : anonymizer.anonymize_text,
    - **list** : anonymizer.anonymize_list,
    - **DataFrame** : anonymizer.anonymize_dataframe,
    - **Series** : anonymizer.anonymize_pd_series
	
----------------------
Stratégies
----------------------

Les stratégies suivantes sont disponibles par défaut : 

- **replace_all_with_tag** : remplace toutes les entités par leur type d'entité.
- **redact_all** : expurge tous les PI 
- **hash_all** : Hache les entités PI
- **mask_all** : Masque toutes les entités DEFAULT
- **scramble_all** : Brouille (change l'ordre des lettres) toutes les entités.
- **mixed_per_entity_type** : {hash : ALPHABET_ENTITIES, mask : SPECIAL_ENTITIES, randomize : NUMERIC_ENTITIES, redact : ALPHANUMERIC_ENTITIES}
- **hash_one** : {hash : [PERSON]}
- **mask_some** : {mask : [PERSON, FULL_ADDRESS], redact : [PHONE_NUMBER]}
- **replace_custom** : {replace : CUSTOM_ENTITIES}
- **redact_custom** : {redact : CUSTOM_ENTITIES}
- **faker_custom** : {faker : CUSTOM_ENTITIES}
- **faker_all** : {faker : DEFAULT_ENTITIES}
- **replace_w_value_custom** : {replace_val : CUSTOM_ENTITIES}

	
Par défaut, la méthode d'anonymisation utilise la stratégie *replace_all_with_tag*, pour utiliser une stratégie différente, utilisez :

.. code:: python
	
	anonymizer.anonymize(text, strategy='redact_all')

	
-----------------------
Langue
-----------------------

Le paramètre **language** indique la langue du texte, par défaut l'anglais, si *None* ou "auto" sont fournis, une recherche sera effectuée pour trouver automatiquement la bonne langue pour chaque entrée de texte pour trouver automatiquement la bonne langue pour chaque texte saisi. Par défaut, Canonym est capable de traiter les textes en anglais et en français.

Dans le cas d'un DataFrame Pandas, Canonym accepte également un dict de format **{nom_de_colonne:langue ou auto, }**, 
afin que chaque colonne puisse être configurée pour une langue différente ou pour une recherche automatique. 

.. code:: python

    # une chaîne de caractères
    anonymizer.anonymize(text, strategy='redact_all', language='fr')
    # un DataFrame Pandas
    anonymizer.anonymize(df, language={'column1' : 'en', 'column2' : 'fr', 'column3' : 'auto'} )

------------------------
Configuration avancée
------------------------

Le comportement de Canonym peut être modifié en éditant les deux fichiers de configuration :
    - ner_config_default.yaml
    - anonymizer_config_default.yaml
    
dans **ner_config_default.yaml** les éléments suivants peuvent être définis :

    - AVAILABLE_LANGS : Les langues que Canonym peut gérer, par défaut *en* et *fr*. 
    - SCORE_THRESHOLD : Le seuil de confiance à partir duquel une entité est étiquetée, par défaut **0.4**.
    - DEFAULT_RECOGNIZERS : Liste des outils de reconnaissance chargés par Canonym 
    - POST_PROCESSING_ENTITIES : Post-traitement spécifique aux entités 
    - PRESIDIO_NLP_ENGINE_CONFIG : Certaines entités seront traitées par un moteur spacy qui doit être défini.
        - nom du moteur nlp
        - modèles      
    - SPACY_ENTITIES :  Liste des entités qui doivent être gérées par Spacy
    - TRANSFORMER_MODELS_ENTITIES :  Liste des entités qui doivent être traitées par les modèles Transformers 
    - TRANSFORMER_MODELS_ENHANCERS :  Amélioration du post-traitement pour les étiquettes fournies par les modèles Transformers (extension des mots partiels ou fusion d'entités contiguës similaires)

dans **anonymizer_config_default.yaml**, les éléments suivants peuvent être définis :

    - AVAILABLE_LANGS :  Les langues que Canonym peut gérer, par défaut *en* et *fr*. 
    - DEFAULT_ENTITIES :  Liste de toutes les entités qui peuvent être anonymisées
    - ALPHABET_ENTITIES : Ensemble d'entités alphabétiques
    - SPECIAL_ENTITIES :  Ensemble d'entités spéciales (email, url, etc.)
    - NUMERIC_ENTITIES :
    - ALPHANUMERIC_ENTITIES :
    - CUSTOM_ENTITIES :  Ensemble personnalisé d'entités à expurger 
    - ALL_ANONYMIZER_STRATEGIES : Liste des stratégies, une stratégie est définie comme suit :
             *nom_de_la_stratégie* : {anonymisation_action_1 : SET_1_OF_ENTITES, anonymisation_action_2 : SET_2_OF_ENTITES}

==========================
Contribuer
==========================
Avant de contribuer merci de lire les instructions présentes dans CONTRIBUTING.md 

lien: [CONTRIBUTING.MD](https://github.com/StatCan/Canonym/blob/main/CONTRIBUTING.md)

==========================
LICENCE
==========================
[MIT License](https://github.com/StatCan/Canonym/blob/main/LICENSE)