<div align="center">
  <img src="https://scontent-cdg4-2.xx.fbcdn.net/v/t39.30808-6/333993870_770478147936292_6413207552341760167_n.jpg?_nc_cat=109&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=jcDPoD_HQ-8Q7kNvwEU8Js_&_nc_oc=AdlteMziC-xJxJsxCjApwjtTWDtaSX-xDUM_aZ3GHfjlDfewRCuqupi_R_03E_TuihaX2IkGe4gfgHHcT-gauW-N&_nc_zt=23&_nc_ht=scontent-cdg4-2.xx&_nc_gid=vWUauW60N9yYu7aK4hQ97w&oh=00_Afe2W864gH16HG9gynq5Px9W8KvztOHOjg4qlj2LyPg8dw&oe=68FDF165" title="SUPINFO" alt="Logo SUPINFO" width="180" />
  <h1>SupKrellM</h1>
  <p width="120"> Script de surveillance système permettant de générer un rapport HTML détaillé sur l’état d’un système Linux, incluant les métriques matérielles, l’utilisation des ressources, l’état des processus, l’activité réseau et les services web, afin de fournir un diagnostic complet du fonctionnement de la machine. </p>
</div>

----

## Télécharger 

[Télécharger le programme](https://github.com/lava1879/SupKrellM/releases/download/v1.0.0/SupKrellM-v1.0.0.zip)

## Configuration matérielle requise
 | Configuration matérielle minimale|Recommendée
----|----|----
Système d'exploitation|Machine virtuelle contenant une distribution de Linux, ou WSL|Ubuntu 25.10
Processeur|Processeur monocœur 32 bits|Processur duocœur 64 bits, ou mieux
RAM (Mémoire)|40 Mo vide|100 Mo vide
Disque (Stockage)|5 Mo vide|100 Mo vide

> [!NOTE]
> C'est possible d'utiliser SupKrellM sur la configuration matérielle minimale, mais la température et l'alimentation (et peut-être d'autres informations) pourrait ne pas apparaître.

**Les autres systèmes d'exploitation (par example, Windows) ne sont pas pris en charge.**

## Arguments de la ligne de commande
 Argument|Fonctionnalité
----|----
--h, -help|Afficher un message d'aide et quitter.
--metrics|Liste des métriques à inclure (system, hardware, memory, disk, process, network, webservices ou all). <br /> Prend en charge plusieurs métriques, par exemple : `python3 main.py --metrics system + hardware`
--output|Nom du fichier HTML de sortie (par défaut: rapport.html)
--dest|Dossier de destination (par défaut: répertoire courant)
--gui|Lance le mode interface graphique en temps réel

## Installation

1. Obtenez le code source soit en [téléchargeant le zip](https://github.com/lava1879/SupKrellM/archive/main.zip), soit en faisant `git clone https://github.com/lava1879/SupKrellM`.
1. Ouvrez le dossier contenant le code source (ou extraire le zip téléchargé et ouvrer le dossier), puis ouvrez le répertoire du programme dans un terminal.
1. Tapez dans le terminal `python3 main.py` pour exécuter le programme et générer la page HTML contenant le rapport système (situé par défaut à la racine du répertoire).

##  Comment ça marche ? 

### Aperçu de l’application de surveillance du système

Cette application Python collecte les métriques du système Linux et les présente soit sous forme de **rapport HTML statique**, soit sous forme de **tableau de bord graphique en temps réel**.

### Collecte des métriques

L’application lit directement les informations du système depuis les répertoires `/proc` et `/sys` de Linux — des répertoires spéciaux exposant les données du noyau sous forme de fichiers texte.

#### Modules de métriques individuels

* **system.py:** Lit `/proc/sys/kernel/hostname`, `/proc/version` et `/proc/uptime` pour obtenir le nom d’hôte, la version du noyau et le temps de fonctionnement (uptime).
* **memory.py:** Analyse `/proc/meminfo` pour extraire les statistiques d’utilisation de la RAM et de la mémoire swap.
* **disk.py:** Lit `/proc/mounts` pour identifier les points de montage des disques, puis exécute la commande `df` afin d’obtenir l’utilisation de chaque partition.
* **process.py:** Lit `/proc/stat` pour l’utilisation CPU, `/proc/cpuinfo` pour les détails du processeur, et parcourt les fichiers `/proc/[pid]/stat` pour lister les processus selon leur consommation CPU.
* **network.py:** Analyse `/proc/net/dev` pour les statistiques des interfaces réseau et `/proc/net/route` pour la passerelle par défaut.
* **hardware.py:** Vérifie `/sys/class/thermal/thermal_zone*/temp` pour les températures et `/sys/class/power_supply/*` pour l’état de la batterie.
* **webservices.py:** Établit des connexions HTTP vers des hôtes spécifiés (par défaut : localhost:80 et localhost:443) et extrait les codes d’état, les en-têtes du serveur et les titres des pages.

### Flux de données

**main.py** → `collect_metrics()` appelle chaque module de métriques → retourne un dictionnaire du type `{"system": {...}, "memory": {...}, ...}` → transmis à **generator.py**

### Génération du rapport HTML

**generator.py:**

1. Reçoit le dictionnaire des métriques
2. Convertit chaque section en listes HTML imbriquées via `_dict_to_html()`
3. Charge **report/template.html**
4. Remplace le champ `{content}` par les sections HTML générées
5. Remplace `{date}` par l’horodatage actuel
6. Écrit le fichier HTML final à l’emplacement spécifié (par défaut: `rapport.html`, possible de changer en utilisant l'argument --output)
7. Le fichier HTML fait référence à `css/main.css` (qui doit se trouver dans un dossier `css/` relatif au fichier HTML)

### Tableau de bord graphique en direct

**dashboard.py:**

* Crée une fenêtre Tkinter avec des sections défilantes
* Lance un thread en arrière-plan exécutant `refresh_loop()`
* Toutes les 2 secondes, appelle les collecteurs de métriques via `collect_all_metrics()`
* Met à jour chaque section du tableau de bord en détruisant les anciens widgets et en créant de nouvelles étiquettes avec les données actuelles
* Code en rouge (`#ffecec`) les erreurs et en blanc les données normales
* Utilise les mêmes modules de métriques que le générateur HTML, offrant ainsi une surveillance en temps réel

Les deux modes de sortie utilisent **les mêmes sources de données**, seule leur présentation diffère (HTML statique vs interface graphique dynamique).

## Objectif du projet

L’objectif principal est de fournir un **outil simple, autonome et éducatif**, permettant d’explorer les mécanismes internes de Linux tout en pratiquant la programmation système en Python.
