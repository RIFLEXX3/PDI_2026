# -*- coding: utf-8 -*-
# Outil Python pour le lissage adaptatif et la génération des courbes de niveau
# Auteurs : CORREC Adélie, GONZO-MASSOL Raphaël, MANDOMBOY Nolvides

import arcpy
from arcpy.ia import *
from arcpy.sa import *

class Lissage(object):
    def __init__(self):
        self.label = "Lissage"
        self.description = "Lissage adaptatif par combinaison de deux MNT"

    def getParameterInfo(self):
        params = []
        
        p0 = arcpy.Parameter(
            displayName="MNT en entrée",
            name="input_raster",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input"
        )
        
        p1 = arcpy.Parameter(
            displayName="MNT ré-échantillonné en sortie",
            name="out_Resample",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output"
        )
        
        p2 = arcpy.Parameter(
            displayName="Taille de rééchantillonage (en mètres)",
            name="resampleSize",
            datatype="GPString",
            parameterType="Required",  
            direction="Input"
        )
        p2.value = "2.5"

        p3 = arcpy.Parameter(
            displayName="Raster calculé de l'écart-type en sortie",
            name="out_SD",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output"
        )

        p4 = arcpy.Parameter(
            displayName="Rayon pour l'écart-type (en cellules)",
            name="radius_SD",
            datatype="GPLong",
            parameterType="Required",
            direction="Input"
        )
        p4.value = 100

        p5 = arcpy.Parameter(
            displayName="Raster Sigmoïde en sortie",
            name="out_Sig",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output"
        )

        p6 = arcpy.Parameter(
            displayName="Coefficient de pente de la sigmoïde (a)",
            name="coef_slop_Sig",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input"
        )
        p6.value = 6

        p7 = arcpy.Parameter(
            displayName="Valeur d'écart-type zones de transition (k)",
            name="transi_SD",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input"
        )
        p7.value = 4

        p8 = arcpy.Parameter(
            displayName="MNT lissé global en sortie",
            name="out_Mean",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output"
        )
    
        p9 = arcpy.Parameter(
            displayName="Type de statistique de lissage",
            name="typ_Stat",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        p9.filter.type = "ValueList"
        p9.filter.list = ["MEAN"]
        p9.value = "MEAN"

        p10 = arcpy.Parameter(
            displayName="Rayon pour le lissage global (en cellules)",
            name="radius_Mean",
            datatype="GPLong",
            parameterType="Required",
            direction="Input"
        )
        p10.value = 20
        
        p11 = arcpy.Parameter(
            displayName="Emplacement du MNT final en sortie",
            name="output_final",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output"
        )

        p12 = arcpy.Parameter(
            displayName='Supprimer les fichiers intermédiaires',
            name='delete_inter',
            datatype='GPBoolean',
            parameterType='Optional',
            direction='Input'
        )
        p12.value = True
        
        params = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12]
        return params
    
    def isLicensed(self):
        return True
    
    def execute(self, parameters, messages):
        arcpy.env.overwriteOutput = True
        arcpy.CheckOutExtension("spatial")
        arcpy.CheckOutExtension("ImageAnalyst")

        in_raster     = parameters[0].valueAsText
        out_Resample  = parameters[1].valueAsText
        
        resample_raw  = parameters[2].valueAsText
        resampleSize  = float(resample_raw.replace(",", "."))
        
        out_SD_path   = parameters[3].valueAsText
        radius_SD     = parameters[4].value
        out_Sig_path  = parameters[5].valueAsText
        coef_slop_Sig = parameters[6].value
        transi_SD     = parameters[7].value
        out_Mean_path = parameters[8].valueAsText
        typ_Stat      = parameters[9].valueAsText
        radius_Mean   = parameters[10].value
        out_raster    = parameters[11].valueAsText 
        delete_inter  = parameters[12].value
              
        nb_etapes = 6 if delete_inter else 5
        arcpy.SetProgressor(
            'Step',
            'Lissage adaptatif en cours...',
            0,
            nb_etapes,
            1
        )
        
        arcpy.SetProgressorLabel("Ré-échantillonnage du MNT...")
        arcpy.management.Resample(
            in_raster,
            out_Resample,
            resampleSize,
            "NEAREST"
        )
        arcpy.SetProgressorPosition()
            
        arcpy.SetProgressorLabel("Calcul de l'écart-type local...")
        sd_raster = arcpy.ia.FocalStatistics(
            out_Resample,
            "Circle " + str(radius_SD) + " CELL",
            "STD",
            "DATA",
            90
        )
        sd_raster.save(out_SD_path)
        arcpy.SetProgressorPosition()

        arcpy.SetProgressorLabel("Normalisation (Sigmoïde)...")
        sig_raster = 1 / (1 + Exp(-coef_slop_Sig * (Raster(out_SD_path) - transi_SD)))
        sig_raster.save(out_Sig_path)
        arcpy.SetProgressorPosition()

        arcpy.SetProgressorLabel("Calcul du lissage global...")
        mean_raster = arcpy.ia.FocalStatistics(
            out_Resample,
            "Circle " + str(radius_Mean) + " CELL",
            typ_Stat,
            "DATA",
            90
        )
        mean_raster.save(out_Mean_path)
        arcpy.SetProgressorPosition()

        arcpy.SetProgressorLabel("Combinaison des rasters...")
        mnt_resampled = Raster(out_Resample)
        final_mnt = mnt_resampled * Raster(out_Sig_path) + (1 - Raster(out_Sig_path)) * Raster(out_Mean_path)
        final_mnt.save(out_raster)
        arcpy.SetProgressorPosition()

        if delete_inter:
            arcpy.SetProgressorLabel('Suppression des fichiers intermédiaires...')
            for path in [out_Resample, out_SD_path, out_Sig_path, out_Mean_path]:
                if arcpy.Exists(path):
                    arcpy.Delete_management(path)
            arcpy.SetProgressorPosition()

        messages.addMessage("Lissage terminé avec succès.")