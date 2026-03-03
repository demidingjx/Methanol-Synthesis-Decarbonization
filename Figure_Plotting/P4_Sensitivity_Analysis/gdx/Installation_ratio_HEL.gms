$Title Technology Installation and Cost Ratio to LCOC

$eolCom //
$Set EL  PEM    
$Set TN  HST
$Set rs  288
$Set Disk F
$Set folder GDX7_M12_Fix
$Set Sens HEL

*输入gdx文件 - Define the gdx file path (GDX1_M12,记得改年份)
$Set Sfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\%folder%\%EL%\Sensitivity\
$Set Dfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\csv_Single_Prov\

*Save folder
$Set Cfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\P4_Sensitivity_Analysis\excel\%EL%\

*-------------------Set define-----------------------------------*
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

Parameter MeOH_Cap_yr(j,i), MeOH_Cap_hr(j,i);   // Caps of methanol plant i in province j [ktonne]
$call csv2gdx %Dfolder%MeOH_Caps.csv  id = MeOH_Cap_yr  index = 1,2  values = 3..lastCol  useHeader = y
$gdxin MeOH_Caps.gdx
$load MeOH_Cap_yr
$gdxin


* ----------------------定义List------------------------------------*
Set pg  / PV, WT, %EL%, LiB, %TN% /
     cons /PV, WT, Grid, %EL%/
    eco / CAPEX, FOM, VOM/
    rg(pg) / PV, WT /
    es(pg) / LiB, %TN% /
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
          P_grid(j,i,h), MeOH_coal_hr(j,i,h), DOI_prov(j)
          LCOM, LCOC,  DLCOR, RLCCE;

$gdxin %Sfolder%S_%EL%_%Sens%.gdx
$load U_nom = U_nom.l, P_PV = P_PV.l, P_WT = P_WT.l, P_EL = P_EL.l, DisP = DisP.l, P_grid = P_grid.l, MeOH_coal_hr = MeOH_coal_hr.l
$load DOI_prov = DOI_prov
$load LCOM = LCOM
$load LCOC = LCOC
$load  DLCOR
$gdxin

* -------------------Consumption -----------------------------------*
Parameter P_PV_sum, P_WT_sum, P_EL_sum, P_grid_sum, Energy(cons);
P_PV_sum = sum((j,ix,h), nds * P_PV(j,ix,h));
P_WT_sum = sum((j,ix,h), nds *  P_WT(j,ix,h));
P_EL_sum = sum((j,i,h),  nds * P_EL(j,i,h));
P_grid_sum = sum((j,i,h), nds *  P_grid(j,i,h));

Energy('PV') = P_PV_sum/1e6;
Energy('WT') = P_WT_sum/1e6;
Energy('%EL%') = P_EL_sum/1e6;
Energy('Grid') = P_grid_sum/1e6;


Display Energy

* ---------------------capacity-----------------------------------*
Scalars     HHV_HST         / 39.36 /    
            HHV_SST         / 2.35 /
            HHV_coal        / 6.11 /;   //MW
Parameter   U_prov_nom(j,pg), U_prov_nom_GW(j,pg);

U_prov_nom(j,'PV') = sum(ix, U_nom(j,ix,'PV'));
U_prov_nom(j,'WT') = sum(ix, U_nom(j,ix,'WT'));
U_prov_nom(j,'%EL%') = sum(ix, U_nom(j,ix,'%EL%'));
U_prov_nom(j,'Lib') = sum(ix, U_nom(j,ix,'Lib'));
U_prov_nom(j,'%TN%') = sum(ix, U_nom(j,ix,'%TN%')) * HHV_%TN%;


U_prov_nom_GW(j,pg) = U_prov_nom(j,pg) / ths;

Display U_prov_nom, U_prov_nom_GW

Parameter U_GW_nom(pg);
U_GW_nom(pg) = sum(j, U_prov_nom_GW(j,pg));

Parameter Ratio;
Ratio = (LCOM-LCOC)/(LCOC) * 100;

*-------------------------LCCR--------------------*
*==========================CO2 BREAKDOWN====================================*
Set yr / 2030, 2040, 2050 /;

Scalar PV_CO2  Carbon emission factor throughout full life cyc of PV [tonne per MWh] / 0.0142 /
       WT_CO2  Carbon emission factor throughout full life cyc of PV [tonne per MWh] / 0.01 / 
       CO2CtM   Carbon emission for each tone of methanol produced [tco2 per tonne] / 4.368 /;

Parameters P_PV(j,ix,h), RLCCE_PV_prov(j)
           P_WT(j,ix,h), RLCCE_WT_prov(j)
           P_grid(j,i,h), RLCCE_grid_prov(j), RLCCE_coal(j)
           M_EL(csp,j,i,h), M_RWS(csp,j,i,h), RLCCE_React_prov(j)
           CO2_em(j,i,h), CF_CO2(j,yr), MeOH_Cap_prov(j);

$call csv2gdx %Dfolder%CEF_grid_yre.csv  id = CF_CO2  index = 1  values = 2..lastCol  useHeader = y
$gdxin CEF_grid_yre.gdx
$load CF_CO2
$gdxin
        
$gdxin %Sfolder%S_%EL%_%Sens%.gdx
$load M_EL = M_EL.l, M_RWS = M_RWS.l, CO2_em = CO2_em.l
$gdxin

MeOH_Cap_prov(j) = sum(i, MeOH_Cap_yr(j,i));

RLCCE_PV_prov(j) = sum((ix,h), nds * P_PV(j,ix,h) * PV_CO2);
RLCCE_WT_prov(j) = sum((ix,h), nds * P_WT(j,ix,h) * WT_CO2);
RLCCE_grid_prov(j) = sum((i,h), nds * CF_CO2(j,'2040') * P_grid(j,i,h));
RLCCE_React_prov(j) = -sum((i,h), nds * (M_EL('CO2',j,i,h) + M_RWS('CO2',j,i,h)));
RLCCE_coal(j) = sum((i,h), nds * CO2_em(j,i,h));
Display RLCCE_PV_prov, RLCCE_WT_prov, RLCCE_grid_prov, RLCCE_React_prov, RLCCE_coal

Parameter amount_PV, amount_WT, amount_grid;
amount_PV = sum((j,ix,h), nds *  P_PV(j,ix,h));
amount_WT = sum((j,ix,h), nds *  P_WT(j,ix,h));
amount_grid = sum((j,i,h), nds *  P_grid(j,i,h));
Display amount_PV, amount_WT, amount_grid;

Parameter Total_grid_ems, Total_CO2_emission;
Total_grid_ems = sum(j, RLCCE_grid_prov(j));
Total_CO2_emission = sum(j,(RLCCE_PV_prov(j) + RLCCE_WT_prov(j) + RLCCE_grid_prov(j)+ RLCCE_React_prov(j) + RLCCE_coal(j)));
Display Total_grid_ems, Total_CO2_emission;

Parameters  CO2_PV, CO2_WT, CO2_grid, CO2_ems;

CO2_PV = sum(j, RLCCE_PV_prov(j));
CO2_WT = sum(j, RLCCE_WT_prov(j));
CO2_grid = sum(j, RLCCE_grid_prov(j));
CO2_ems = sum(j, RLCCE_coal(j));

Display CO2_PV, CO2_WT, CO2_grid, CO2_ems

sets cc / PV, WT, Grid, Electrification, Coal/;

Parameter CO2_cost(cc);
CO2_cost('PV') = CO2_PV / (sum(j, MeOH_Cap_prov(j) * ths * DOI_prov(j)));
CO2_cost('WT') = CO2_WT / (sum(j, MeOH_Cap_prov(j) * ths * DOI_prov(j)));
CO2_cost('Grid') = CO2_grid / (sum(j, MeOH_Cap_prov(j) * ths * DOI_prov(j)));
CO2_cost('Electrification') = CO2_ems / (sum(j, MeOH_Cap_prov(j) * ths * DOI_prov(j)));
CO2_cost('Coal') =0;

Display CO2_cost;

* =======================Decarbonization cost=================================*
Parameter Decar_cost;
RLCCE = (CO2_PV + CO2_WT + CO2_grid + CO2_ems)/sum((j,i), MeOH_Cap_yr(j,i) * ths);

Decar_cost = DLCOR / MAX(0.00001, (CO2CtM - RLCCE)) ;

Display RLCCE;
Display Decar_cost;
* ------------------Write in Excel: Nom-------------------*
Execute_Unload 'Data_%EL%_%Sens%.gdx';
$onEcho > Prov_nom.txt
Par = U_prov_nom_GW          rng = GW_tech!A1       rDim = 1
Par = U_GW_nom                  rng = Capacity!A1
Par = Energy                        rng = Energy_TWh!A1
Text = "LCOM"                      rng = Ratio!A1
Par = LCOM                          rng = Ratio!A2

Text = "LCOC"                      rng = Ratio!B1
Par = LCOC                          rng = Ratio!B2

Text = "Ratio"                      rng = Ratio!C1
Par = Ratio                          rng = Ratio!C2

Text = 'LCCR'                      rng = Ratio!D1
Par = Decar_cost                 rng = Ratio!D2
$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw Data_%EL%_%Sens%.gdx output = %Cfolder%Data_%EL%_%Sens%.xlsx @Prov_nom.txt';
