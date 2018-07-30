import os
import xml.etree.ElementTree as ETree
from DoiGenerator import lastDoiNumber, increment_doi
from Parse import parserRecord
from API_DataCite_Metadata import enregistrer_metadonneesRessource, enregistrer_metadonneesPhrase
from API_DataCite_DOI import enregistrer_url_doiRessource, enregistrer_url_doiPhrase
from API_Get_DataCite_DOI import get_doi
from constantes import NAMESPACES, CRITICAL_LOG, PARSE_FILE, DOI_PREFIX
from parserAnnotation import parseAnnotation
from Phrase import Phrase
import logging
import sys

logging.basicConfig(filename=CRITICAL_LOG, level=logging.INFO)

# Récupération du paramétre au lancement du programme
if len(sys.argv) == 1:
    print("Paramètre manquant. Renseigner add pour traiter uniquemnt les nouvelles ressources ou add_update pour traiter les nouvelles ressources et faire les mises à jour pour le reste des fichiers")
else:
    parameter = sys.argv[1]


    # Teste si le paramètre est correctement renseigné
    if parameter != 'add_update' and parameter != 'add':
        print("Paramètre incorrect. Renseigner add ou add_update")
    else:

        # creation et suppression d'un dossier et de son contenu
        """
        shutil.rmtree("test")
        shutil.rmtree("testURL")
        shutil.rmtree("testPhrase")
        shutil.rmtree("testURL_Phrase")
        os.remove("critical.log")
        
        os.mkdir("test")
        os.mkdir("testURL")
        os.mkdir("testPhrase")
        os.mkdir("testURL_Phrase")
        open('critical.log','w')
        """

        # on utilise la fonction lastDoiNumber pour obtenir le dernier numero DOI
        last_doi_number = lastDoiNumber(PARSE_FILE)


        # --------Parse.py OAI-PMH avec etree--------#
        tree = ETree.parse(PARSE_FILE)
        root = tree.getroot()
        nouvelleLIste = 0

        # parsing du fichier xml
        for index, record in enumerate(root.findall(".//oai:record", NAMESPACES)):

            # on utilise la fonction parserRecord pour parser chaque record et créer un objet record
            objetRecord = parserRecord(record)

            # --------gestion de la reprise après le premier lancement--------#
            # si le doi n'existe pas ou on veut faire une mise à jour d'une ressource existante, on recrée la ressources
            if objetRecord.doiIdentifiant == "" or parameter == "add_update":

                # si l'identifiant n'existe pas et on veut seulement ajouter les nouveaux identifiants sans mise à jour
                if objetRecord.doiIdentifiant == "":

                    # le numéro doi va continuer la numéroation du dernier numéro doi, auquel on rajoute des 0
                    doiNumber, last_doi_number = increment_doi(last_doi_number)

                    # on atttribue à l'objet record créée le numéro doi complet avec le prefixe,
                    # en utilisant une nouvelle affectation à l'attribut identifiant de l'objet.
                    objetRecord.doiIdentifiant = DOI_PREFIX+doiNumber

                """
                # on utilise la methode build de la classe Record pour créer le fichier xml
                fichier_xmlRessource = objetRecord.build()

                 # on utilise la fonction generatorFichierUrlDoi pour créer les fichiers avec les url et les DOI
                fichier_textRessource = objetRecord.generatorFichierUrlDoi()

               
                # methodes pour interroger l'API de Datacite et enregistrer le fichier de metadonnées et le fichier text avec l'url et le doi pour les ressources
                if fichier_xmlRessource:
                    enregistrer_metadonneesRessource(fichier_xmlRessource, objetRecord.doiIdentifiant)
        
                if fichier_textRessource:
                    enregistrer_url_doiRessource(fichier_textRessource, objetRecord.doiIdentifiant)
                """

                # ---------------------------- PARSING ANNOTATION ---------------------#
        
                # extraire le lien url pour chaque fichier xml
                if objetRecord.lienAnnotation:
                    # on appelle la fonction parseAnnotation pour récupérer une liste avec les id des phrases
                    listeId, type = parseAnnotation(objetRecord.lienAnnotation)

                    if listeId:
                        tailleUneliste = len(listeId)
                        print (tailleUneliste, objetRecord.lienAnnotation)
                        nouvelleLIste = nouvelleLIste + tailleUneliste
        
                        # pour chaque id, on génère un numéro doi, un fichier xml et un fichier text
                        for indexid, id in enumerate(listeId):

                            # numéro DOI de la phrase
                            if type == "sentence":
                                affixe = "S" + str(indexid+1)
                            elif type == "word":
                                affixe = "W" + str(indexid+1)
                            doiPhrase = objetRecord.doiIdentifiant + "." + affixe

                            """
                            # création du fichier xml pour chaque phrase
                            objetPhrase = Phrase(id, doiPhrase, affixe, objetRecord)
                            fichier_xmlPhrase = objetPhrase.buildMetadataPhrase()
        
                            # création du fichier text avec le DOI et l'URL de la phrase
                            fichier_textPhrase = objetPhrase.generatorFichierUrlDoiPhrase()
        
                            # methodes pour interroger l'API de Datacite et enregistrer le fichier de metadonnées et le fichier text avec l'url et le doi pour les phrases
                            if fichier_xmlPhrase:
                                enregistrer_metadonneesPhrase(fichier_xmlPhrase, id)
        
                            if fichier_textPhrase:
                                enregistrer_url_doiPhrase(fichier_textPhrase, doiPhrase, id)
        
                            # limite le nombre d'itérations pour la phrase et le mot pour tester.
                            # mettre en commentaire pour faire fonctionner sur la totalité de l'annotation
                            if indexid == 3:
                                break
                            """
                else:
                    message = "La ressource {} ne contient pas de fichier d'annotations".format(objetRecord.identifiantOAI)
                    logging.info(message)

            # limite le nombre d'itérations pour la ressource.
            # mettre en commentaire pour faire fonctionner sur la totalité du fichier Cocoon
            if index == 6000:
               break
        #print(nouvelleLIste)




    """
    control = False
    if os.stat("mapping_oai_doi.csv").st_size == 0:
       with open("mapping_oai_doi.csv", "w", newline='') as mapping:
           spamwriter = csv.writer(mapping, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
           spamwriter.writerow([objetRecord.identifiantOAI[21:], objetRecord.identifiant])
       control = True
    if control == True:
       with open("mapping_oai_doi.csv", newline='') as mappingread:
           spamreader = csv.reader(mappingread, delimiter=' ', quotechar='|')
           for row in spamreader:
               if row[0] == objetRecord.identifiantOAI[21:] and row[1] == objetRecord.identifiant_DOI_Cocoon[4:]:
                   print("L'oai correspond au doi")
    
    with open("mapping_oai_doi.csv", newline='') as mappingread:
       spamreader = csv.reader(mappingread, delimiter=' ', quotechar='|')
       for row in spamreader:
           if [objetRecord.identifiantOAI[21:], objetRecord.identifiant_DOI_Cocoon[4:]] not in spamreader:
                   print ("On peut les rajouter")
                   with open("mapping_oai_doi.csv", "a", newline='') as mapping:
                       spamwriter = csv.writer(mapping, delimiter=' ', quotechar='|',
                                               quoting=csv.QUOTE_MINIMAL)
                       spamwriter.writerow([objetRecord.identifiantOAI[21:], objetRecord.identifiant])
                       break
           else:
               print("le mapping oai-doi existe déja")
    """