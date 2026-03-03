$Title Processing relevant gdx to cost breakdown

$eolCom //
$Set EL  SOE
$Set TN  SST
$Set YR  2050
$Set ED  ED25
$Set rs  288
$Set Disk E
$Set folder GDX7_M12_Fix
*输出excel文件 - Define the output excel location (LCOM，年份)
$Set Cfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\Results_new\%EL%\%YR%\%ED%\

*输入gdx文件 - Define the gdx file path (GDX1_M12,记得改年份)
$Set Sfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\%folder%\%EL%\%YR%\%ED%\

* ----------------------定义省份与城市-----------------------------*
$Set Dfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\csv_Single_Prov\

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

alias (jx,j);
* ----------------------定义List------------------------------------*
Set pg  / PV, WT, %EL%, Lib, %TN% /
    eco / CAPEX, FOM, VOM/
    rg(pg) / PV, WT /
    es(pg) / Lib, %TN% /
    ln     / AC, DC /
    t      / h0 * h%rs% /
    h(t)   / h1 * h%rs% /
    csp    / H2, O2, H2O, CO2, Gas, MeOH /;
    
Scalars  nhs   number hours in a year    / 8760 /
         ths   thousand                 / 1.0e+3 /
         mms   million                  / 1.0e+6 /
         nds   number of typical days;

nds = nhs / %rs%;


*=================================Size======================================================*
*---------------------读数据----------------------------*
Parameter U_nom(j,ix,pg), P_PV(j,ix,h), P_WT(j,ix,h), P_EL(j,i,h), DisP(es,j,i,h)
          P_grid(j,i,h), MeOH_coal_hr(j,i,h), DOI_prov(j);

$gdxin %Sfolder%S_%EL%_%YR%_%ED%.gdx
$load U_nom = U_nom.l, P_PV = P_PV.l, P_WT = P_WT.l, P_EL = P_EL.l, DisP = DisP.l, P_grid = P_grid.l, MeOH_coal_hr = MeOH_coal_hr.l
$load DOI_prov = DOI_prov
$gdxin

* -------------------处理 Grid 与 coal -----------------------------------*
Parameter U_grid_nom(j,i), U_coal_nom(j,i);

U_grid_nom(j,i) = smax(h, P_grid(j,i,h));
U_coal_nom(j,i) = smax(h, MeOH_coal_hr(j,i,h));

Display U_grid_nom, U_coal_nom

* ---------------------capacity-----------------------------------*
Scalars     HHV_HST         / 39.36 /    
            HHV_SST         / 2.35 /
            HHV_coal        / 6.11 /;   //MW
Parameter   U_prov_nom(j,pg), U_prov_nom_GW(j,pg)
            Size_nom(j), Percent_nom(j,pg), M_ST_nom(j);

U_prov_nom(j,'PV') = sum(ix, U_nom(j,ix,'PV'));
U_prov_nom(j,'WT') = sum(ix, U_nom(j,ix,'WT'));
U_prov_nom(j,'%EL%') = sum(ix, U_nom(j,ix,'%EL%'));
U_prov_nom(j,'Lib') = sum(ix, U_nom(j,ix,'Lib'));
U_prov_nom(j,'%TN%') = sum(ix, U_nom(j,ix,'%TN%')) * HHV_%TN%;
M_ST_nom(j) = sum(ix, U_nom(j,ix,'%TN%'));
*U_prov_nom(j,'Grid') = sum(i, U_grid_nom(j,i));
*U_prov_nom(j,'Coal') = sum(i, U_coal_nom(j,i)) * HHV_coal;

U_prov_nom_GW(j,pg) = U_prov_nom(j,pg) / ths;
Size_nom(j) = sum(pg,U_prov_nom_GW(j,pg));
Percent_nom(j,pg) = U_prov_nom_GW(j,pg) / Size_nom(j);

Display U_prov_nom, U_prov_nom_GW, Size_nom, Percent_nom, M_ST_nom

* -------------------annual contribution-----------------------------------*
Parameter U_yr_prov(j,pg), U_yr_prov_TWh(j,pg)
          Size_yr(j), Percent_yr(j,pg);

U_yr_prov(j,'PV') = sum((ix,h), nds * P_PV(j,ix,h));
U_yr_prov(j,'WT') = sum((ix,h), nds * P_WT(j,ix,h));
U_yr_prov(j,'%EL%') = sum((i,h), nds * P_EL(j,i,h));
U_yr_prov(j,'LiB') = sum((i,h), nds * DisP('LiB',j,i,h));
U_yr_prov(j,'%TN%') = sum((i,h), nds * DisP('%TN%',j,i,h))* HHV_%TN%;
*U_yr_prov(j,'Grid') = sum((i,h), nds * P_grid(j,i,h));
*U_yr_prov(j,'Coal') = sum((i,h), nds * MeOH_coal_hr(j,i,h)) * HHV_coal;

U_yr_prov_TWh(j,pg) = U_yr_prov(j,pg)/ ths /ths;
Size_yr(j) = sum(pg,U_yr_prov_TWh(j,pg));
Percent_yr(j,pg) = U_yr_prov_TWh(j,pg) / Size_nom(j);

Display U_yr_prov, U_yr_prov_TWh, Size_yr, Percent_yr

* ------------------Write in Excel: Nom-------------------*
Execute_Unload 'Nom_size_%EL%_%YR%_%ED%.gdx';
$onEcho > Prov_nom.txt
Text = "Prov"                rng = Total_size!A1
Text = "Total_size"          rng = Total_size!B1
Par = Size_nom               rng = Total_size!A2    rDim = 1
Par = Percent_nom            rng = Portion!A1       rDim = 1
Par = U_prov_nom_GW          rng = GW_tech!A1       rDim = 1
Par = M_ST_nom              rng = ST_mass!A1        rDim = 1

Text = "Prov"                rng = ED_prov!A1
Text = "ED_prov"             rng = ED_prov!B1
Par = DOI_prov               rng = ED_prov!A2       rDim = 1

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw Nom_size_%EL%_%YR%_%ED%.gdx output = %Cfolder%Nom_size_%EL%_%YR%_%ED%.xlsx @Prov_nom.txt';

* ------------------Write in Excel: yr-------------------*
Execute_Unload 'Yr_size_%EL%_%YR%_%ED%.gdx';
$onEcho > Prov_Yr.txt
Text = "Prov"                rng = Total_size!A1
Text = "Total size"          rng = Total_size!B1
Par = Size_Yr                rng = Total_size!A2    rDim = 1
Par = Percent_Yr             rng = Portion!A1       rDim = 1
Par = U_yr_prov_TWh          rng = TWh_tech!A1       rDim = 1

Text = "Prov"                rng = ED_prov!A1
Text = "ED_prov"             rng = ED_prov!B1
Par = DOI_prov               rng = ED_prov!A2       rDim = 1


$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw Yr_size_%EL%_%YR%_%ED%.gdx output = %Cfolder%Yr_%EL%_%YR%_%ED%.xlsx @Prov_Yr.txt';

*=================================TNS_LINE======================================================*
*---------------------读数据----------------------------*
Parameter P_city_PV(j,ix,i,h), P_city_WT(j,ix,i,h),
          P_exp_PV(j,ix,h), P_exp_WT(j,ix,h), P_imp(j,ix,h), F_prov(ln,jx,j,h);

$gdxin %Sfolder%S_%EL%_%YR%_%ED%.gdx
$load P_city_PV = P_city_PV.l, P_city_WT = P_city_WT.L
$load P_exp_PV = P_exp_PV.l, P_exp_WT = P_exp_WT.l, P_imp = P_imp.l, F_prov = F_prov.l
$gdxin

*----------------------TNS_nom----------------------------*
Parameter U_PV_city(j,ix,i), U_WT_city(j,ix,i), U_PV_exp(j,ix), U_WT_exp(j,ix)
          U_imp(j,ix), U_prov(ln,jx,j) ;

U_PV_city(j,ix,i) = smax(h, P_city_PV(j,ix,i,h)) / ths;
U_WT_city(j,ix,i) = smax(h, P_city_WT(j,ix,i,h)) / ths;
U_PV_exp(j,ix) = smax(h, P_exp_PV(j,ix,h)) / ths;
U_WT_exp(j,ix) = smax(h, P_exp_WT(j,ix,h)) / ths;
U_imp(j,ix) = smax(h, P_imp(j,ix,h)) / ths;
U_prov(ln,jx,j) = smax(h, F_prov(ln,jx,j,h)) / ths;

Display U_PV_city, U_WT_city, U_PV_exp, U_WT_exp, U_imp, U_prov


*----------------------TNS_nom----------------------------*
Parameter U_yr_PV_city(j,ix,i), U_yr_WT_city(j,ix,i), U_yr_PV_exp(j,ix), U_yr_WT_exp(j,ix),
          U_yr_imp(j,ix), U_annual_prov(ln,jx,j);

U_yr_PV_city(j,ix,i) = sum(h, P_city_PV(j,ix,i,h)) / ths;
U_yr_WT_city(j,ix,i) = sum(h, P_city_WT(j,ix,i,h)) / ths;
U_yr_PV_exp(j,ix) = sum(h, P_exp_PV(j,ix,h)) / ths;
U_yr_WT_exp(j,ix) = sum(h, P_exp_WT(j,ix,h)) / ths;
U_yr_imp(j,ix) = sum(h, P_imp(j,ix,h)) / ths;
U_annual_prov(ln,jx,j) = sum(h, F_prov(ln,jx,j,h)) / ths;

Display U_yr_PV_city, U_yr_WT_city, U_yr_PV_exp, U_yr_WT_exp, U_yr_imp, U_annual_prov

* ------------------Write in Excel: TNS_nom-------------------*
Execute_Unload 'TNS_nom_%EL%_%YR%_%ED%.gdx';
$onEcho > TNS.txt
Text = "Prov"                rng = U_PV_city!A1
Text = "City_ix"             rng = U_PV_city!B1
Text = "City_i"              rng = U_PV_city!C1
Text = "Value"               rng = U_PV_city!D1
Par = U_PV_city              rng = U_PV_city!A2       rDim = 3

Text = "Prov"                rng = U_WT_city!A1
Text = "City_ix"             rng = U_WT_city!B1
Text = "City_i"              rng = U_WT_city!C1
Text = "Value"               rng = U_WT_city!D1
Par = U_WT_city              rng = U_WT_city!A2       rDim = 3

Text = "Prov"               rng = U_PV_exp!A1
Text = "City"                rng = U_PV_exp!B1
Text = "Value"               rng = U_PV_exp!C1
Par = U_PV_exp               rng = U_PV_exp!A2        rDim = 2

Text = "Prov"                rng = U_WT_exp!A1
Text = "City"                rng = U_WT_exp!B1
Text = "Value"               rng = U_WT_exp!C1   
Par = U_WT_exp               rng = U_WT_exp!A2        rDim = 2

Text = "Prov"                rng = U_imp!A1
Text = "City"                rng = U_imp!B1
Text = "Value"               rng = U_imp!C1  
Par = U_imp                  rng = U_imp!A2           rDim = 2


Text = "Type"                rng = U_prov!A1
Text = "Prov_jx"             rng = U_prov!B1
Text = "Prov"                rng = U_prov!C1
Text = "Value"               rng = U_prov!D1
Par = U_prov                 rng = U_prov!A2          rDim = 3


$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw TNS_nom_%EL%_%YR%_%ED%.gdx output = %Cfolder%TNS_nom_%EL%_%YR%_%ED%.xlsx @TNS.txt';


* ------------------Write in Excel: TNS_yr-------------------*
Execute_Unload 'TNS_yr_%EL%_%YR%_%ED%.gdx';
$onEcho > TNS_yr.txt
Text = "Prov"                rng = U_PV_city!A1
Text = "City_ix"             rng = U_PV_city!B1
Text = "City_i"              rng = U_PV_city!C1
Text = "Value"               rng = U_PV_city!D1
Par = U_yr_PV_city           rng = U_PV_city!A2       rDim = 3

Text = "Prov"                rng = U_WT_city!A1
Text = "City_ix"             rng = U_WT_city!B1
Text = "City_i"              rng = U_WT_city!C1
Text = "Value"               rng = U_WT_city!D1
Par = U_yr_WT_city           rng = U_WT_city!A2       rDim = 3

Text = "Prov"                rng = U_PV_exp!A1
Text = "City"                rng = U_PV_exp!B1
Text = "Value"               rng = U_PV_exp!C1
Par = U_yr_PV_exp            rng = U_PV_exp!A2        rDim = 2

Text = "Prov"                rng = U_WT_exp!A1
Text = "City"                rng = U_WT_exp!B1
Text = "Value"               rng = U_WT_exp!C1   
Par =U_yr_WT_exp             rng = U_WT_exp!A2        rDim = 2

Text = "Prov"                rng = U_imp!A1
Text = "City"                rng = U_imp!B1
Text = "Value"               rng = U_imp!C1  
Par = U_yr_imp               rng = U_imp!A2           rDim = 2


Text = "Type"                rng = U_prov!A1
Text = "Prov_jx"             rng = U_prov!B1
Text = "Prov"                rng = U_prov!C1
Text = "Value"               rng = U_prov!D1
Par = U_annual_prov          rng = U_prov!A2          rDim = 3
  

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw TNS_yr_%EL%_%YR%_%ED%.gdx output = %Cfolder%TNS_yr_%EL%_%YR%_%ED%.xlsx @TNS_yr.txt'