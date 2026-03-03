
$Title Processing relevant gdx to csv

$eolCom //
$Set ED  ED100
$Set EL  PEM
$Set Disk E
$Set folder GDX7_M12_Fix

$Set tl  288
$Set rs  288
$Set el  PEM
$Set ys  2030           //year
$Set yl  5              //interest rate
$Set Scn BLN       //BLN, CN60
$Set TOU 1.02249   //Electricity price
Sets g      / PV, WT, PEM, SOE, LiB, HST, SST, RWS, MSR /
     t      / h0 * h%tl% /
     h(t)   / h1 * h%tl% /;


*输出excel文件 - Define the output excel location (LCOM，年份)
$Set Lfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Results_M12_0812\%EL%\%ED%\

*输入gdx文件 - Define the gdx file path (%folder%,记得改年份)
$Set Dfolder E:\2025_Methanol_synthesis\3_GAMS\csv_Single_Prov\

$Set Sfolder_2030 %Disk%:\2025_Methanol_synthesis\3_GAMS\%folder%\%EL%\%ys%\%ED%\




Scalars  nhs   number hours in a year    / 8760 /
         ths   thousand                 / 1.0e+3 /
         mms   million                  / 1.0e+6 /
         nds   number of typical days;
*==================================================================
Sets j(*)    province with methanol produciton
     ix(*)   city with renewable energy generation;
     
$call csv2gdx %Dfolder%Provinces.csv  id = j  index = 1  useHeader = y 
$gdxIn Provinces.gdx
$load j
$gdxin

$call csv2gdx %Dfolder%Cities.csv  id = ix  index = 1  useHeader = y 
$gdxIn Cities.gdx
$load ix
$gdxin

Sets i(ix)  citis with methanol synthesis plants;
$call csv2gdx %Dfolder%Cities_w_MeOH.csv  id = i  index = 1  useHeader = y 
$gdxIn Cities_w_MeOH.gdx
$load i
$gdxin

Sets irx(ix)  citis without methanol synthesis plants;
$call csv2gdx %Dfolder%Cities_wo_MeOH.csv  id = irx  index = 1  useHeader = y 
$gdxIn Cities_wo_MeOH.gdx
$load irx
$gdxin

Parameters tou(j,h);
$call csv2gdx %Dfolder%Electricity_%tl%.csv  id = tou  index = 1  values = 2..lastCol  useHeader = y
$gdxin Electricity_%tl%.gdx
$load tou
$gdxin

Alias (j,jx);    // Provinces
Alias (i,iim);   // iim, cities with methanol plants

Display j, ix, irx, i, iim;

Parameter MeOH_Cap_yr(j,i), MeOH_Cap_hr(j,i);   // Caps of methanol plant i in province j [ktonne]
$call csv2gdx %Dfolder%MeOH_Caps.csv  id = MeOH_Cap_yr  index = 1,2  values = 3..lastCol  useHeader = y
$gdxin MeOH_Caps.gdx
$load MeOH_Cap_yr
$gdxin

MeOH_Cap_hr(j,i) = MeOH_Cap_yr(j,i) * ths / nhs;   // kton/yr convert to tonne/hr

Display MeOH_Cap_yr, MeOH_Cap_hr;


//=============================计算LCOM—CITY======================================
alias (js,j);


Sets plt(j,i)         Methanol synthesis plant i in province j
