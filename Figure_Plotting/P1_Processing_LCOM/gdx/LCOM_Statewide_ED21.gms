$Title Processing relevant gdx to csv

$eolCom //
$Set ED  ED21
$Set EL  PEM
$Set Disk E
$Set folder GDX7_M12_Fix
*输出excel文件 - Define the output excel location (LCOM，年份)
$Set Lfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Results_M12_0812\%EL%\%ED%\

*输入gdx文件 - Define the gdx file path (%folder%,记得改年份)
$Set Sfolder_2030 %Disk%:\2025_Methanol_synthesis\3_GAMS\%folder%\%EL%\2030\%ED%\

$Set Sfolder_2040 %Disk%:\2025_Methanol_synthesis\3_GAMS\%folder%\%EL%\2040\%ED%\

$Set Sfolder_2050 %Disk%:\2025_Methanol_synthesis\3_GAMS\%folder%\%EL%\2050\%ED%\

* --------------------Case  2030--------------------------------*
$onEcho > howToWrite_S_2030.txt

Text = "Levelized_cost"      rng = 2030_LCOM!A1
Text = "Value"               rng = 2030_LCOM!B1 

Text = "Coal_LCOM"         rng = 2030_LCOM!A2
Par = LCOC                 rng = 2030_LCOM!B2

Text = "State_LCOM"        rng = 2030_LCOM!A3
Par = LCOM                 rng = 2030_LCOM!B3

Text = "Levelized_CO2_emission"       rng = 2030_RLCCE!A1
Text = "Value"                        rng = 2030_RLCCE!B1 

Text = "State_CO2e"                   rng = 2030_RLCCE!A2
Par = RLCCE                           rng = 2030_RLCCE!B2

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2030%S_%EL%_2030_%ED%.gdx output = %Lfolder%LCOM_%EL%_%ED%.xlsx @howToWrite_S_2030.txt';
 
$onEcho > howToWrite_P_2030.txt

Text = "Prov_LCOM"           rng = 2030_LCOM!A4
Par = LCOM.l                 rng = 2030_LCOM!B4 

Text = "Prov_RLCCE"           rng = 2030_RLCCE!A3
Par = RLCCE                  rng = 2030_RLCCE!B3 

Text = "Prov_LCOM_j"          rng = 2030_Prov_LCOM_j!A1     
Text = "Value"                rng = 2030_Prov_LCOM_j!B1 
Par = LCOM_prov               rng = 2030_Prov_LCOM_j!A2     rDim = 1

Text = "Prov_RLCCE_j"         rng = 2030_Prov_RLCCE_j!A1     
Text = "Value"                rng = 2030_Prov_RLCCE_j!B1 
Par = RLCCE_prov              rng = 2030_Prov_RLCCE_j!A2     rDim = 1

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2030%P_%EL%_2030_%ED%.gdx output = %Lfolder%LCOM_%EL%_%ED%.xlsx @howToWrite_P_2030.txt';

$onEcho > howToWrite_C_2030.txt

Text = "City_LCOM"           rng = 2030_LCOM!A5
Par = LCOM.l                 rng = 2030_LCOM!B5 
Text = "City_RLCCE"           rng = 2030_RLCCE!A4
Par = RLCCE.l                rng = 2030_RLCCE!B4 

Text = "City_LCOM_j"          rng = 2030_City_LCOM_j!A1
Text = "Value"                rng = 2030_City_LCOM_j!B1 
Par = LCOM_prov               rng = 2030_City_LCOM_j!A2     rDim = 1

Text = "City_LCOM_j"          rng = 2030_City_RLCCE_j!A1
Text = "Value"                rng = 2030_City_RLCCE_j!B1 
Par = RLCCE_prov               rng = 2030_City_RLCCE_j!A2     rDim = 1

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2030%C_%EL%_2030_%ED%.gdx output = %Lfolder%LCOM_%EL%_%ED%.xlsx @howToWrite_C_2030.txt';

* --------------------Case  2040--------------------------------*
$onEcho > howToWrite_S_2040.txt

Text = "Levelized_cost"      rng = 2040_LCOM!A1
Text = "Value"               rng = 2040_LCOM!B1 

Text = "Coal_LCOM"         rng = 2040_LCOM!A2
Par = LCOC                 rng = 2040_LCOM!B2

Text = "State_LCOM"        rng = 2040_LCOM!A3
Par = LCOM                 rng = 2040_LCOM!B3

Text = "Levelized_CO2_emission"       rng = 2040_RLCCE!A1
Text = "Value"                        rng = 2040_RLCCE!B1 

Text = "State_CO2e"                   rng = 2040_RLCCE!A2
Par = RLCCE                           rng = 2040_RLCCE!B2


$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2040%S_%EL%_2040_%ED%.gdx output = %Lfolder%LCOM_%EL%_%ED%.xlsx @howToWrite_S_2040.txt';


$onEcho > howToWrite_P_2040.txt

Text = "Prov_LCOM"           rng = 2040_LCOM!A4
Par = LCOM.l                 rng = 2040_LCOM!B4 

Text = "Prov_RLCCE"           rng = 2040_RLCCE!A3
Par = RLCCE                  rng = 2040_RLCCE!B3 


Text = "Prov_LCOM_j"          rng = 2040_Prov_LCOM_j!A1     
Text = "Value"                rng = 2040_Prov_LCOM_j!B1 
Par = LCOM_prov               rng = 2040_Prov_LCOM_j!A2     rDim = 1

Text = "Prov_RLCCE_j"         rng = 2040_Prov_RLCCE_j!A1     
Text = "Value"                rng = 2040_Prov_RLCCE_j!B1 
Par = RLCCE_prov              rng = 2040_Prov_RLCCE_j!A2     rDim = 1

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2040%P_%EL%_2040_%ED%.gdx output = %Lfolder%LCOM_%EL%_%ED%.xlsx @howToWrite_P_2040.txt';

$onEcho > howToWrite_C_2040.txt

Text = "City_LCOM"           rng = 2040_LCOM!A5
Par = LCOM.l                 rng = 2040_LCOM!B5
Text = "City_RLCCE"           rng = 2040_RLCCE!A4
Par = RLCCE                  rng = 2040_RLCCE!B4 


Text = "City_LCOM_j"          rng = 2040_City_LCOM_j!A1
Text = "Value"                rng = 2040_City_LCOM_j!B1 
Par = LCOM_prov               rng = 2040_City_LCOM_j!A2     rDim = 1

Text = "City_LCOM_j"          rng = 2040_City_RLCCE_j!A1
Text = "Value"                rng = 2040_City_RLCCE_j!B1 
Par = RLCCE_prov               rng = 2040_City_RLCCE_j!A2     rDim = 1

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2040%C_%EL%_2040_%ED%.gdx output = %Lfolder%LCOM_%EL%_%ED%.xlsx @howToWrite_C_2040.txt';

* --------------------Case  2050--------------------------------*
$onEcho > howToWrite_S_2050.txt

Text = "Levelized_cost"      rng = 2050_LCOM!A1
Text = "Value"               rng = 2050_LCOM!B1 

Text = "Coal_LCOM"         rng = 2050_LCOM!A2
Par = LCOC                 rng = 2050_LCOM!B2

Text = "State_LCOM"        rng = 2050_LCOM!A3
Par = LCOM                 rng = 2050_LCOM!B3

Text = "Levelized_CO2_emission"       rng = 2050_RLCCE!A1
Text = "Value"                        rng = 2050_RLCCE!B1 

Text = "State_CO2e"                   rng = 2050_RLCCE!A2
Par = RLCCE                           rng = 2050_RLCCE!B2

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2050%S_%EL%_2050_%ED%.gdx output = %Lfolder%LCOM_%EL%_%ED%.xlsx @howToWrite_S_2050.txt';


$onEcho > howToWrite_P_2050.txt

Text = "Prov_LCOM"           rng = 2050_LCOM!A4
Par = LCOM.l                 rng = 2050_LCOM!B4

Text = "Prov_RLCCE"           rng = 2050_RLCCE!A3
Par = RLCCE                  rng = 2050_RLCCE!B3 

Text = "Prov_LCOM_j"          rng = 2050_Prov_LCOM_j!A1     
Text = "Value"                rng = 2050_Prov_LCOM_j!B1 
Par = LCOM_prov               rng = 2050_Prov_LCOM_j!A2     rDim = 1

Text = "Prov_RLCCE_j"         rng = 2050_Prov_RLCCE_j!A1     
Text = "Value"                rng = 2050_Prov_RLCCE_j!B1 
Par = RLCCE_prov              rng = 2050_Prov_RLCCE_j!A2     rDim = 1

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2050%P_%EL%_2050_%ED%.gdx output = %Lfolder%LCOM_%EL%_%ED%.xlsx @howToWrite_P_2050.txt';

$onEcho > howToWrite_C_2050.txt

Text = "City_LCOM"           rng = 2050_LCOM!A5
Par = LCOM.l                 rng = 2050_LCOM!B5
Text = "City_RLCCE"           rng = 2050_RLCCE!A4
Par = RLCCE                  rng = 2050_RLCCE!B4 


Text = "City_LCOM_j"          rng = 2050_City_LCOM_j!A1
Text = "Value"                rng = 2050_City_LCOM_j!B1 
Par = LCOM_prov               rng = 2050_City_LCOM_j!A2     rDim = 1

Text = "City_LCOM_j"          rng = 2050_City_RLCCE_j!A1
Text = "Value"                rng = 2050_City_RLCCE_j!B1 
Par = RLCCE_prov               rng = 2050_City_RLCCE_j!A2     rDim = 1
$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2050%C_%EL%_2050_%ED%.gdx output = %Lfolder%LCOM_%EL%_%ED%.xlsx @howToWrite_C_2050.txt';

