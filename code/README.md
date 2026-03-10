# Description du fonctionnement de la toolbox  
## Outil : Génération des courbes de niveau

Cette toolbox ArcGIS contient plusieurs outils de traitement.  
cette section ne décrit que l’outil **Générer courbes de niveau**.

Cet outil permet de produire automatiquement des **courbes de niveau cartographiquement propres** à partir d’un **MNT (Modèle Numérique de Terrain)**.

Le traitement comprend les étapes suivantes :

- rééchantillonnage du MNT  
- calcul des courbes de niveau  
- simplification géométrique  
- lissage cartographique  
- orientation des courbes  
- préparation pour la symbologie  

---

# 1. Exemple d’appel de l’outil en Python

L’outil peut être exécuté directement depuis **ArcGIS Pro** ou via **ArcPy**.

```python
arcpy.ImportToolbox(r"C:\Users\VHeau\Documents\ArcGIS\Projects\demo_arcgis\demo_arcgis.atbx")

arcpy.courbes.GenererCourbes(
    mnt_entree=r"E:\Suivi_GEODEV_2026\data\MNT1.tif",
    cell_size=1,
    simplify_tolerance=5,
    smooth_tolerance=15,
    simplify_tolerance_bis=5,
    gdb_sortie=r"C:\Users\VHeau\Documents\ArcGIS\Projects\demo_arcgis\demo_arcgis.gdb",
    equidistance=5,
    longueur_min=20,
    nom_sortie="Courbes_MNT_1"
)
```

---

# 2. Paramètres de l’outil

| Paramètre | Description |
|---|---|
| MNT en entrée | Raster représentant le modèle numérique de terrain utilisé pour calculer les courbes de niveau |
| Taille de rééchantillonnage | Résolution cible du MNT après rééchantillonnage |
| Tolérance SimplifyLine | Tolérance utilisée pour simplifier la géométrie des courbes |
| Tolérance SmoothLine | Tolérance utilisée pour lisser les courbes |
| Tolérance SimplifyLine après lissage | Deuxième simplification appliquée après le lissage |
| Géodatabase de sortie | Géodatabase dans laquelle seront stockées les couches intermédiaires |
| Équidistance des courbes | Intervalle altimétrique entre deux courbes |
| Longueur minimale des courbes | Filtre optionnel pour supprimer les courbes trop courtes |
| Nom de la couche finale | Nom de la classe d’entités générée |

---

# 3. Description détaillée du traitement

Le processus de génération des courbes de niveau est composé de plusieurs étapes.

---

## 3.1 Rééchantillonnage du MNT

La première étape consiste à **rééchantillonner le MNT**.

Outil utilisé :  
**Resample**

Objectifs :

- adapter la résolution du MNT  
- réduire les artefacts  
- homogénéiser la précision altimétrique  

Méthode utilisée : **NEAREST**

Sortie intermédiaire : **TMP_Resample**

---

## 3.2 Calcul des courbes de niveau

Les courbes de niveau sont générées à partir du MNT rééchantillonné.

Outil utilisé : **ContourWithBarriers**

Paramètres principaux :

- équidistance des courbes  
- intervalle des courbes maîtresses  
- génération de polylignes  

Sortie intermédiaire : **TMP_Courbes**

Le champ **Contour** est ensuite renommé en **Altitude**.

---

## 3.3 Simplification des courbes

Les courbes générées contiennent souvent un grand nombre de sommets.

Une **simplification géométrique** est appliquée afin de :

- réduire le nombre de points  
- améliorer les performances  
- conserver la forme générale  

Outil utilisé : **SimplifyLine**

Méthode : **POINT_REMOVE**

Sortie : **TMP_CourbesFilt**

---

## 3.4 Lissage cartographique

Les courbes sont ensuite **lissées** afin d’obtenir un rendu cartographique plus naturel.

Outil utilisé : **SmoothLine**

Méthode : **PAEK**

Ce traitement permet :

- d’adoucir les angles  
- d’améliorer la lisibilité cartographique  

Sortie : **TMP_CourbesSmooth**

---

## 3.5 Seconde simplification

Après le lissage, une **seconde simplification** est appliquée afin de :

- supprimer les sommets introduits par le lissage  
- optimiser la géométrie finale  

Outil utilisé : **SimplifyLine**

Sortie : **TMP_CourbesFinal**

---

## 3.6 Classification des courbes

Un champ nommé **SYMBO** est ajouté.

Ce champ permet de distinguer les types de courbes :

| Type | Valeur |
|---|---|
| Courbe normale | CNV_NORMALE |
| Courbe maîtresse | CNV_MAITRESSE |
| Courbe intercalaire | CNV_INTERCALAIRE |

Cette classification permet une **symbologie automatique dans ArcGIS**.

---

## 3.7 Orientation des courbes

Pour garantir une représentation cohérente du relief, les courbes doivent être **orientées correctement**.

Principe :

- l’altitude située à gauche de la courbe doit être **plus élevée** que celle située à droite.

Méthode :

1. création d’un buffer à gauche et à droite des courbes maîtresses  
2. calcul de l’altitude moyenne dans chaque buffer  
3. comparaison des altitudes  

Outils utilisés :

- Buffer  
- ZonalStatisticsAsTable  
- JoinField  

Si l’orientation est incorrecte, l’outil **FlipLine** est utilisé pour inverser la géométrie.

---

## 3.8 Champ d’orientation pour la symbologie

Un champ nommé **ANGLE** est ajouté.

Valeurs possibles :

| Valeur | Signification |
|---|---|
| 0 | orientation normale |
| 180 | courbe inversée |

Ce champ permet d’orienter correctement certains symboles cartographiques.

---

## 3.9 Export de la couche finale

La couche finale est exportée dans la géodatabase avec le nom défini par l’utilisateur.

Exemple : **Courbes_MNT_1**

Cette couche contient :

- les courbes de niveau  
- leur altitude  
- leur classification  
- leur orientation  

---

# 4. Nettoyage des données intermédiaires

Les couches temporaires suivantes sont supprimées automatiquement :

- TMP_Resample  
- TMP_Courbes  
- TMP_CourbesFilt  
- TMP_CourbesSmooth  
- TMP_CourbesFinal  
- TMP_Courbes_G  
- TMP_Courbes_D  
- TMP_AltMoy_G  
- TMP_AltMoy_D  

---

# 5. Résultat final

Le résultat final est une **classe d’entités de type polyligne** contenant :

- des courbes de niveau cartographiquement propres  
- une géométrie optimisée  
- une classification pour la symbologie  
- une orientation correcte  

