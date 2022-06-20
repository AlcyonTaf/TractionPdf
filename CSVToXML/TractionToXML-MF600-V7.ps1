####################################################################################
#                                                                                  #
# Script pour la conversion des résultats de traction au format CSV vers XLM       #
#                                                                                  #
#  TODO : Faire description du fontionnement
#  TODO : Voir pour faire la comparaison entre nbr de fichier CSV en entré et Nombre de fichier xml généré
#  TODO : Voir comment gerer erreur lors de la création des groupes suite a lecture du fichier avec mauvais encoding
#
# Version :
# V5 : Modification du regroupement qui prenait en compte le nom du fichier ce qui pose probleme avec les TRZ 
# V6 : Essai pour rajouter un fichier de statistique pour savoir le nombre d'essai transmis et les erreurs
# V7 : Ajout d'une vérification de l'encodage des fichiers, du nom du fichier, et vérification sur longueur max a transmettre a SAP
#
# Format du fichier d'export pour la machine de traction MF :
#   
#

#############
# Variables #
#############
# Pour stopper l'execution en cas d'erreur
$ErrorActionPreference = 'stop'

# Date de l'export 
$DateExport = Get-Date -Format "dd-MM-yy"

#Date - Heure pour log
# Ok, j'avoue ce n'est pas vraiment un Timestamp :)
#$(Get-TimeStampLog) = Get-Date -Format "dd_MM_yy_-_HH_mm_ss "
function Get-TimeStampLog {
    
  return "[{0:dd/MM/yy} {0:HH:mm:ss}]" -f (Get-Date)
  
}
function Get-TimeStamp {
    
  return "{0:yyyyMMddHHmmssffff}" -f (Get-Date)
  
}

# Emplacement du fichier script
$global:ScriptPath = split-path -parent $MyInvocation.MyCommand.Definition

#Tableau des tractions avec les résultats
$tabTractions = @()

#Contenue de la balise <Source>
$SourceSAP = "LABO_IC"

#Gestion des parametres qualitatifs dans SAP
$ParaQualSAP = '990', '560', '561'


#######
# Log #
#######
#Dossier des logs
$LogFolder = $ScriptPath + "\log"
#$LogFile = New-Item -type file ($LogFolder + "\log_" + (Get-Date -Format FileDateTime) + ".txt") -Force
$LogFile = $LogFolder + "\log_" + (Get-Date -Format FileDateTime) + ".txt"
#Start-Transcript -Append $LogFile
Start-Transcript -Path $LogFile

# Dossier contenant les fichiers CSV
#$TractionCSVFolder = $ScriptPath + "\ExportTraction"
$TractionCSVFolder = "C:\Users\CRMC\PycharmProjects\TractionPdf\ExportSAP"

### Gestion des dossiers de suivi ###
## On va créer un dossier par jour, puis un dossier error-csv, csv , xml, logs
## exemple : Export du dd-MM-yy\error-csv, \csv, \xml, \logs
try {
  #Dossier Export du dd-MM-yy
  $ExportFolder = New-Item -ItemType Directory -Force -Path ($ScriptPath + "\Suivi\Export du " + $DateExport) -ErrorAction Stop
  Write-Output ($(Get-TimeStampLog) + "Création du dossier " + ($ExportFolder.Name) + " => OK")

  #Dossier des .csv ayant généré une erreure
  $ErrorCsvFolder = New-Item -ItemType Directory -Force -Path ($ExportFolder.FullName + "\error-csv") -ErrorAction Stop
  Write-Output ($(Get-TimeStampLog) + "Création du dossier " + ($ErrorCsvFolder.Name) + " => OK")

  #Dossier d'archive des .csv correctement traité
  $ArchiveCsvFolder = New-Item -ItemType Directory -Force ($ExportFolder.FullName + "\CSV") -ErrorAction Stop
  Write-Output ($(Get-TimeStampLog) + "Création du dossier " + ($ArchiveCsvFolder.Name) + " => OK")

  # Dossier ou vont devoir etre enregistrer les .xml pour transfert SAP
  # Soit en local et FileDispatcher fais le transfert +copie
  # Soit directement sur un répertoire partagé
  # Dans l'idéal il faut les créer dans un dossier temporaire puis les déplacer dans le dossier d'export
  # \XML\ et \XML\ToSAP
  # Pour test :
  #$ExportXMLFolder = $ScriptPath + "\XML"

  #Dossier des .xml généré
  $XMLFolder = New-Item -ItemType Directory -Force ($ExportFolder.FullName + "\XML") -ErrorAction Stop
  Write-Output ($(Get-TimeStampLog) + "Création du dossier " + ($XMLFolder.Name) + " => OK")

  #Dossier des .xml a transférer vers SAP
  #TODO : il ne sert a rien de créer ce dossier => modification pour le mettre en fixe sans création, faire vérification qu'il existe avant
  $XMLToSAPFolder = "C:\Users\CRMC\PycharmProjects\TractionPdf\CSVToXML\ToSAP"

  #Dossier des .xml copié
  $XMLToSAPCopieFolder = New-Item -ItemType Directory -Force ($ExportFolder.FullName + "\XML\CopieXML") -ErrorAction Stop
  Write-Output ($(Get-TimeStampLog) + "Création du dossier " + ($XMLToSAPCopieFolder.Name) + " => OK")

  #Dossier pour les stats:
  $StatFolder = New-Item -ItemType Directory -Force ($ScriptPath + "\Stat") -ErrorAction Stop
  Write-Output ($(Get-TimeStampLog) + "Création du dossier " + ($StatFolder.Name) + " => OK")
} 
catch {
  Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Probleme lors de la création des dossiers : " + $_)
}

########
# Stat #
########
# Date de l'export pour stat 
$DateExportStat = Get-Date -Format "dd-MM-yy_HH-mm-ss"

function Set-Stat {
  [CmdletBinding()]
  param (
    [string]$DateExecution,
    [string]$UMFichierOk,
    [string]$UMFichierNok,
    [string]$UMEssaiOk,
    [string]$UMEssaiNok
  )

  $Statfile = $ScriptPath + "\Stat\Stat.csv"
  $StatData = @()

  $StatData += [PSCustomObject]@{
    Date          = $DateExecution;
    FichierErreur = $UMFichierNok;
    FichierOK     = $UMFichierOk;
    EssaiErreur   = $UMEssaiNok;
    EssaiOK       = $UMEssaiOk
  }

  $StatData | Export-Csv -Path $Statfile -Delimiter ";" -NoTypeInformation -Append

}

############
# Encodage #
############

#Function trouvé sur interne et modifier carles fichiers ne contiennent pas de BOM.
function Get-Encoding {
  param
  (
    [Parameter(Mandatory, ValueFromPipeline, ValueFromPipelineByPropertyName)]
    [Alias('FullName')]
    [string]
    $Path
  )

  process {
    $bom = New-Object -TypeName System.Byte[](4)
        
    $file = New-Object System.IO.FileStream($Path, 'Open', 'Read')
    
    $null = $file.Read($bom, 0, 4)
    $file.Close()
    $file.Dispose()
    
    $enc = [Text.Encoding]::ASCII
    $bom
    if ($bom[0] -eq 0x2b -and $bom[1] -eq 0x2f -and $bom[2] -eq 0x76) 
    { $enc = [Text.Encoding]::UTF7 }
    if ($bom[0] -eq 0xff -and $bom[1] -eq 0xfe) 
    { $enc = [Text.Encoding]::Unicode }
    if ($bom[0] -eq 0xfe -and $bom[1] -eq 0xff) 
    { $enc = [Text.Encoding]::BigEndianUnicode }
    if ($bom[0] -eq 0x00 -and $bom[1] -eq 0x00 -and $bom[2] -eq 0xfe -and $bom[3] -eq 0xff) 
    { $enc = [Text.Encoding]::UTF32 }
    if ($bom[0] -eq 0xef -and $bom[1] -eq 0xbb -and $bom[2] -eq 0xbf) 
    { $enc = [Text.Encoding]::UTF8 }
    # Ajout pour tenir compte de nos fichier qui on 1 byte sur 2 = 0 quand l'encodage change
    if ($bom[1] -eq 0 -and $bom[3] -eq 0)
    { $enc = [Text.Encoding]::BigEndianUnicode }
        
    [PSCustomObject]@{
      Encoding = $enc
      Path     = $Path
    }
  }
}

#################
# Templates XML #
#################

$MainTemplate = @'
<?xml version="1.0" encoding="ISO-8859-1"?>
<__Essais>
  <__Essai>
    <Source>$($SourceSAP)</Source>
    <TimeStamp>$($TimeStamp)</TimeStamp>
    <NoCommande>$($NumCommande)</NoCommande>
    <NoPoste>$($NumPoste)</NoPoste>
    <SapOf />
    <Batch>$($NumLot)</Batch>
    <NumPlaque></NumPlaque>
    <NumPlaqueMQ></NumPlaqueMQ>
    <StatutPlaque></StatutPlaque>
    <DateStatutPlaque></DateStatutPlaque>
    <RemStatPlaque />
    <SequenceLoc>$($NumSeqLoc)</SequenceLoc>
    <Eprouvettes>
      $($Eprouvettes -join "`n")
    </Eprouvettes>
    <OperationCode />
    <OperationUser />
    <OperationDate />
    <OperationTime />
  </__Essai>
</__Essais>
'@

#Template pour chaque Eprouvettes (Essai en réalité)
$EprouvettesTemplate = @'
      <Eprouvette>
        <SeqEssais>$($NumSeqEssais)</SeqEssais>
        <TypeEssai></TypeEssai>
        <Temperature></Temperature>
        <UnitTemp></UnitTemp>
        <EtatRef></EtatRef>
        <StatutEpr></StatutEpr>
        <DateStatutEpr></DateStatutEpr>
        <RemStatEpr />
        <TTHs>
        </TTHs>
        <Parametres>
        $($Parametre -join "`n")
        </Parametres>
      </Eprouvette>
'@

#Template pour chaque résultat
$ParametreTemplate = @'
          <Parametre>
            <NumPara>$($NumParaSAP)</NumPara>
            <UnitPara />
            <ValuePara>$($ValParaSAP)</ValuePara>
            <ValueParaT>$($ValParaSAPT)</ValueParaT>
            <SequenceResult>$($ValSeqResult)</SequenceResult>
            <SequenceEssEpr>$($ValSeqEssEpr)</SequenceEssEpr>
          </Parametre>
'@

##########
# Script #
##########

### Lecture des fichiers .csv et archivage ### 
Write-Output ($(Get-TimeStampLog) + "*** Lecture des fichiers de tractions ***")
Get-ChildItem $TractionCSVFolder\*.csv | ForEach-Object {
  Write-Output ($(Get-TimeStampLog) + "Lecture du fichier " + ($_.Name))
  
  #Vérification du Nom de fichier : Cela permet de dégager les fichiers générer sans méthode QR-Code
  #La taille doit etre de 3 une fois decouper par '-'
  $LengthFileName = ($_.Name -split ('-')).Length
  #$LengthFileName
  #Vérification de l'encodage des fichiers
  #Comme je n'ai rencontré que 2 cas je vérifie uniquement ceux ci
  $GetCSVEncoding = Get-Encoding($_.FullName)

  if ($GetCSVEncoding.Encoding -eq [Text.Encoding]::BigEndianUnicode) {
    Write-Output ($(Get-TimeStampLog) + "Encodage détecté : UNICODE ")
    $CSVEncoding = "UNICODE"
  }
  elseif ($GetCSVEncoding.Encoding -eq [Text.Encoding]::ASCII) {
    Write-Output ($(Get-TimeStampLog) + "Encodage détecté : ASCII ")
    $CSVEncoding = "ASCII"
  }
  else {
    $CSVEncoding = "INCONNU"
  }

  #Si le fichier n'est pas dans le bon encodage on ne le traite pas et on le déplace
  if ($CSVEncoding -eq "INCONNU") {
    #Cas ou l'encodage n'est pas bon, on ne traite pas le fichier 
    Set-Stat -DateExecution $DateExportStat -UMFichierNOk $_.BaseName

    #Il faut l'indiquer dans le log
    Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Probleme lors de lecture du fichier : " + $_.BaseName)
    Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Détails de l'erreur : Encodage non connu " )
    #On essai de la deplacer dans le dossier error-csv
    Move-Item -Path $_.FullName -Destination ($ErrorCsvFolder.FullName + "\" + $_.BaseName + "-EncodingErreur-" + $(Get-TimeStamp) + ".csv")
    if ($?) {
      Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier en erreur " + $_.Name + " dans le dossier \archive\error-csv ==> OK")
    }
    else {
      Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier en erreur " + $_.Name + " dans le dossier \archive\error-csv ==> NOK")
    }
  }
  #Vérification du nom de fichier
  elseif ($LengthFileName -ne 3) {
    #Cas ou le nom du fichier n'est pas bon, on ne traite pas le fichier 
    Set-Stat -DateExecution $DateExportStat -UMFichierNOk $_.BaseName

    #Il faut l'indiquer dans le log
    Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Probleme lors de lecture du fichier : " + $_.BaseName)
    Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Détails de l'erreur : Le nom du fichier n'est pas correct " )
    #On essai de la deplacer dans le dossier error-csv
    Move-Item -Path $_.FullName -Destination ($ErrorCsvFolder.FullName + "\" + $_.BaseName + "-NomFichierErreur-" + $(Get-TimeStamp) + ".csv")
    if ($?) {
      Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier en erreur " + $_.Name + " dans le dossier \archive\error-csv ==> OK")
    }
    else {
      Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier en erreur " + $_.Name + " dans le dossier \archive\error-csv ==> NOK")
    }
  }
  else {
    #Vérification OK, on lie le fichier et on le deplace
    try {
      $NbrLigne = (Get-Content $_.FullName -Encoding $CSVEncoding  | Measure-Object -Line).Lines # <== Unicode sur mon PC mais sur la machine de traction ASCII ? bizarre ma fonctionne
      if ($NbrLigne -eq 1) {
        #$contenue = Get-Content $_.FullName 
        $SplitRow = (Get-Content $_.FullName -Encoding $CSVEncoding) -split (';') # <== Unicode sur mon PC mais sur la machine de traction ASCII ? bizarre ma fonctionne
        #$splitrow
        $tabTractions += [pscustomobject]@{ NumCommande = $SplitRow[0];
          NumPoste                                      = $SplitRow[1];
          NumLot                                        = $SplitRow[2];
          NumSeqLoc                                     = $SplitRow[3];
          NumSeqEssais                                  = $SplitRow[4];
          NbrEpr                                        = $SplitRow[5];
          FileName                                      = $_.Name                                        
          ResultsTraction                               = $SplitRow[6..($SplitRow.Length - 1)] 
        } # <-- 2 car pour l'instant il y a une valeur vide
        # Le fichier est traité on le deplace dans l'archive CSV
        #TODO : Pour l'instant je met le nom du fichier entier a voir par la suite
        Set-Stat -DateExecution $DateExportStat -UMFichierOk $_.BaseName
    
        Write-Output ($(Get-TimeStampLog) + "Lecture du fichier " + ($_.Name) + " OK")
        Move-Item -Path $_.FullName -Destination ($ArchiveCsvFolder.FullName + "\" + $_.BaseName + "-" + $(Get-TimeStamp) + ".csv")
        if ($?) {
          Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier " + ($_.Name) + " dans le \archive\csv ==> Ok")
        }
        else {
          Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier " + ($_.Name) + " dans le \archive\csv ==> NOk")
        }
      }
      else {
        #Cas ou il y a plus d'une seul ligne ce qui n'est pas normale => il faut alerter 
        #On deplace le fichier dans le dossier error des csv
        Set-Stat -DateExecution $DateExportStat -UMFichierNOk $_.BaseName
    
        Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Plusieurs ligne dans le même fichier : " + $_.Name)
        Move-Item -Path $_.FullName -Destination ($ErrorCsvFolder.FullName + "\" + $_.BaseName + "-ErrorMultipleLine-" + $(Get-TimeStamp) + ".csv")
        if ($?) {
          Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier en erreur " + $_.Name + " dans le dossier \archive\error-csv ==> OK")
        }
        else {
          Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier en erreur " + $_.Name + " dans le dossier \archive\error-csv ==> NOK")
        }
      }
    }
    Catch {
      #Cas ou on n'a pas réussi a ouvrir le fichier ou a le traiter pour l'ajouter dans le tableau
      Set-Stat -DateExecution $DateExportStat -UMFichierNOk $_.BaseName
    
      #Il faut l'indiquer dans le log
      Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Probleme lors de lecture du fichier : " + $_.BaseName)
      Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Détails de l'erreur : " + $_)
      #On essai de la deplacer dans le dossier error-csv
      Move-Item -Path $_.FullName -Destination ($ErrorCsvFolder.FullName + "\" + $_.BaseName + "-ErreurLectureFichier-" + $(Get-TimeStamp) + ".csv")
      if ($?) {
        Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier en erreur " + $_.Name + " dans le dossier \archive\error-csv ==> OK")
      }
      else {
        Write-Output ($(Get-TimeStampLog) + "Déplacement du fichier en erreur " + $_.Name + " dans le dossier \archive\error-csv ==> NOK")
      }
      
    }
  }
}

Write-Output ($(Get-TimeStampLog) + "*** L'ensemble des fichiers de traction sont traités ***")

### Vérification traitement de tous les fichiers ###
# a ce stade il ne doit plus rester de fichier dans le dossier, on peut vérifier pour etre certain
# TODO


### Création de group en fonction de l'ID SAP pour identifier les essais qui doivent etre regroupés dans le .xml ###
Write-Output ($(Get-TimeStampLog) + "*** Création des XML ***")
$tabTractions | Group-Object -Property NumCommande, NumPoste, NumLot, NumSeqLoc, NumSeqEssais, NbrEpr | ForEach-Object {
  try {
    Write-Output ($(Get-TimeStampLog) + "Group-Object depuis le tableau des tractions")
    $_
    #$_.count
    #$_.Group.NumCommande

    #On extrait du nom du groupe les infos de l'ID SAP, plus simple car peut etre de type string ou object en fonction du nombre
    $SplitIdSAP = $_.Name -split (', ')
    $NumCommande = $SplitIdSAP[0]
    $NumPoste = $SplitIdSAP[1]
    $NumLot = $SplitIdSAP[2]
    $NumSeqLoc = $SplitIdSAP[3]
    $NumSeqEssais = $SplitIdSAP[4]
    $NbrEpr = $SplitIdSAP[5]

    $Parametre = ''

    #On va récupérer le nom du fichier a ce moment pour ensuite extraire la date et l'heure du nom quand on va traiter les parametres
    #Dans le cas des Traction Z il y aura plusieur fichier, donc on récupére uniquement le 1er nom.
    if ($_.Group.FileName -is [string]) {
      $FileName = $_.Group.FileName
    }
    else {
      $FileName = $_.Group.FileName[0]
    }

    # On va vérifier ici si le nombre de fichier correspond au nombre de mesure, car il peut y avoir plusieurs échantillons mesuré pour le même essai 
    If ($_.Count -ne $NbrEpr) {
      Set-Stat -DateExecution $DateExportStat -UMEssaiNok $FileName.Replace(".csv", "")

      Write-Output "***ERREUR*** Le nombre d'essai n'est pas égal au nbr attendu : " $FileName
    }
    else {
      Write-Output ($(Get-TimeStampLog) + "Vérification du nombre d'essai ok")
      #On va créer une tableau objet pour regrouper les parametre (type de mesure, ex : Rp0.2) et leur valeur 
      $tabParaSAP = @()
      $_.Group.ResultsTraction | ForEach-Object {
            
        $SplitResult = $_ -split (':')
        $SplitResultValParaSAP = $SplitResult[2]
        $SplitResultNumParaSAP = $SplitResult[0]
          
        #On va vérifier que les valeur des para SAP ne dépasse pas une certainne longueur
        #Par exemple pour les TRZ le EYoung a une valeur abérante qu'il ne faut pas transmettre a SAP, on vérifie également qu'il ne s'agissent pas d'un para qualitatif
        If ($SplitResultValParaSAP.Length -gt 6 -and -not ($ParaQualSAP.Contains($SplitResultNumParaSAP))) {
          Write-Output ($(Get-TimeStampLog) + "***ATTENTION*** la valeur du Para SAP " + $SplitResultNumParaSAP + " dépasse la valeur max de 6 : " + $SplitResultValParaSAP)
          $SplitResultValParaSAP = 0
          Write-Output ($(Get-TimeStampLog) + "***ATTENTION*** la valeur du Para SAP " + $SplitResultNumParaSAP + " changé pour 0")
        }

        $tabParaSAP += [pscustomobject]@{ NumParaSAP = $SplitResultNumParaSAP;
          ValParaSAP                                 = $SplitResultValParaSAP;
          ValSeqResult                               = 1;
          ValSeqEssEpr                               = 1
        } 
      } 
        
      # On Boucle sur les groups de Parametre SAP
      Write-Output ($(Get-TimeStampLog) + "Boucle sur les résultats des fichiers de tractions")      
      $tabParaSAP | Group-Object -Property NumParaSAP | ForEach-Object {
        $count = 1
        #On boucle sur le contenue des groups et on compte pour la valeur ValSeqEssEpr
        foreach ($val in $_.Group) {
          #Write-Output "on est dans la boucle"
          #$count
          #$val.NumParaSAP
          #$val.ValParaSAP
              
          #Définition des variables de Here-String $ParametreTemplate
          #TODO : Vérifier ici les parametre qualitatif afin de compléter la bonne variables
          $NumParaSAP = $val.NumParaSAP
          #$NumParaSAP
          # On vérifier si la valeur du para SAP fait partie des qualitatif
          if ($ParaQualSAP.Contains($NumParaSAP)) {
            # Rajout de la date dans le para 561 = Date réalisation essai. Format YYYYMMDDHHMMSS
            if ($NumParaSAP -eq "561") {
              # Parfois les opérateurs rajoute des info apres l'UM, ce qui modifie le debut du nom du fichier. La partie date et heure reste fixe.
              # On enleve donc le debut par la différence de la taille total - 18 cara pour la date et heure + extension
              $DateEssaiString = $FileName.Substring($FileName.Length - 18).replace(".csv", "")
              $DateEssai = [DateTime]::ParseExact($DateEssaiString, "dd.MM.yy-HH_mm", $null)
              $ValParaSAPT = $DateEssai.ToString("yyyyMMddHHmmss")
              $ValParaSAP = ""
            }
            else {
              $ValParaSAPT = $val.ValParaSAP
              $ValParaSAP = ""
            }
            Write-Output ($(Get-TimeStampLog) + "Création du Noeud XML <Parametre> Qualitatif avec NumParaSAP =" + $NumParaSAP + " - ValParaSAPT =" + $ValParaSAPT + " - ValSeqEssEpr =" + $ValSeqEssEpr + " - ValSeqResult =" + $ValSeqResult)
          }
          else {
            #Cas normal ou pas de para qualitatif
            $ValParaSAP = $val.ValParaSAP
            $ValParaSAPT = ""
            Write-Output ($(Get-TimeStampLog) + "Création du Noeud XML <Parametre> avec NumParaSAP =" + $NumParaSAP + " - ValParaSAP =" + $ValParaSAP + " - ValSeqEssEpr =" + $ValSeqEssEpr + " - ValSeqResult =" + $ValSeqResult)
          }
          #On compte pour savoir si il y a plusieur éprouvette dans le cas des TRZ
          $ValSeqResult = $count
          #$ValSeqEssEpr tout le temps égale a 1 pour traction
          $ValSeqEssEpr = $val.ValSeqEssEpr
              
          $Parametre += $ExecutionContext.InvokeCommand.ExpandString($ParametreTemplate)
          $count++
        }
      }   
      #Ensuite les groupe éprouvettes, mais je pense tous le temps 1
      #$Eprouvettes = ''
      Write-Output ($(Get-TimeStampLog) + "Création du Noeud XML <Eprouvette>")
      $Eprouvettes = $ExecutionContext.InvokeCommand.ExpandString($EprouvettesTemplate)
      #On finit par le groupe principal, mise en forme du xml et enregistrement dans le répertoire temporaire avant transfert
      #$test =  $ExecutionContext.InvokeCommand.ExpandString($MainTemplate)
      #$test
      # Timestamp
      $TimeStamp = $(Get-TimeStamp)
      Write-Output ($(Get-TimeStampLog) + "Création du Noeud XML Root, mise en forme et enregistrement du fichier xml")
      $xml = [xml] $ExecutionContext.InvokeCommand.ExpandString($MainTemplate)
      #Création du fichier dans le dossier d'enregistrement
      $xml.Save($XMLFolder.FullName + "\IC_PL_ESS_RES_" + $NumCommande + "_" + $NumPoste + "_" + $NumLot.replace('.', '_') + "_" + $NumSeqLoc + "_" + $TimeStamp + ".xml")
      
      Set-Stat -DateExecution $DateExportStat -UMEssaiok $FileName.Replace(".csv", "")
    }
    
  }
  catch {
    Set-Stat -DateExecution $DateExportStat -UMEssaiNok $FileName.Replace(".csv", "")
    Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Probleme lors la création du xml : " + $_)
  }
}
Write-Output ($(Get-TimeStampLog) + "*** Fin du traitement des fichiers ***")


### déplacement des fichiers dans le répertoire ToSAP ###
# Peut etre voir pour le faire fichier par fichier et enregistrer dans un log que ok ?
# Apparition d'un message d'erreur comme quoi le fichier est utilisé par un autre processus? voir pour changer le fonctionnement comme indiqué ligne du dessus
Write-Output ($(Get-TimeStampLog) + "*** Debut de la copie des XML généré dans le Dossier TOSAP ***")
Get-ChildItem $XMLFolder\*.xml | ForEach-Object {
  Write-Output ($(Get-TimeStampLog) + "*** Déplacement de " + $_.Name + "***")
  #Copie du fichier vers PIR
  try {
    Copy-Item -Path $_.FullName -Destination $XMLToSAPFolder
  } 
  catch {
    Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Echec de la copie du fichier vers le dossier TOSAP")
  }
  #Déplacement du fichier dans archive
  try {
    Move-Item -Path $_.FullName -Destination $XMLToSAPCopieFolder
  } 
  catch {
    Write-Output ($(Get-TimeStampLog) + "***ERREUR*** Echec du deplacement du fichier vers le dossier TOSAP")
  }
}
Write-Output ($(Get-TimeStampLog) + "*** Fin de la copie des XML généré dans le Dossier TOSAP ***")

#######
# Log #
#######
# On arrete les logs de la session
Stop-Transcript