$Title Processing relevant gdx to cost breakdown

$eolCom //
$Set EL  SOE
$Set TN  SST
$Set YR  2050
$Set ED  ED76
$Set DOI  0.76
$Set rs  288
$Set TP  C
$Set Disk E
$Set folder GDX7_M12_Fix
*输出excel文件 - Define the output excel location (LCOM，年份)
$Set Cfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED\Results_new\%EL%\%YR%\

*输入gdx文件 - Define the gdx file path (GDX1_M12,记得改年份)
$Set Sfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\%folder%\%EL%\%YR%\%ED%\

*BAU gdx 文件
$Set Bfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED\Results_new\%EL%\%YR%\

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

alias (js,j);
* ----------------------定义List------------------------------------*
Set cb / PV, WT, %EL%, Lib, %TN%, TNS, Grid, H2O, O2, CO2, OM_coal, Coal  /
    cbd / PV_CAP, PV_OM, WT_CAP, WT_OM, %EL%_CAP, %EL%_OM, Lib_CAP, Lib_OM, %TN%_CAP, %TN%_OM, RWS_CAP, RWS_OM, TNS, Grid, H2O, O2, CO2e, CO2p, CO2c, OM_coal, Coal, OM_Msyn  /
    eco / CAPEX, FOM, VOM/
    rg(cb) / PV, WT /
    es(cb) / Lib, %TN% /
    ln / AC, DC /
    t      / h0 * h%rs% /
    h(t)   / h1 * h%rs% /
    csp    / H2, O2, H2O, CO2, Gas, MeOH /;
    
Scalars  nhs   number hours in a year    / 8760 /
         ths   thousand                 / 1.0e+3 /
         mms   million                  / 1.0e+6 /
         nds   number of typical days;

nds = nhs / %rs%;

Parameter
    Capex_RE(rg,j,ix), FOM_RE(rg,j,ix)
    Capex_EL(j,i), FOM_EL(j,i), VOM_EL(j,i)
    Capex_RWS(j,i), FOM_RWS(j,i), VOM_RWS(j,i)
    Capex_ES(es,j,i), FOM_ES(es,j,i), VOM_ES(es,j,i)
    VOM_Pcity(j,ix,i), VOM_Pprov(ln,js,j)
    E_purs(j,i), FSC_H2O(j,i), FSC_O2(j,i), FSC_CO2(j,i)
    TFSC_CO2e(j), TFSC_CO2p(j), TFSC_CO2c(j), TFSC_CO2(j)
    FSC_cwater_prov(j), FSC_eC_prov(j)
    FOM_coal(j), VOM_coal(j), FSC_coal_prov(j)
    FOM_Msyn_prov(j), VOM_Msyn_prov(j)
    DOI_prov(j), DOI
    MeOH_Cap_prov(j)
    FSC_CO2e_city_woi(j,i)
    DLCOR, RLCCE;


$gdxin %Sfolder%%TP%_%EL%_%YR%_%ED%.gdx
$load Capex_RE = Capex_RE.l, FOM_RE = FOM_RE.l
$load Capex_EL = Capex_EL.l, FOM_EL = FOM_EL.l, VOM_EL = VOM_EL.l
$load Capex_ES = Capex_ES.l, FOM_ES = FOM_ES.l, VOM_ES = VOM_ES.l
$load E_purs = E_purs.l
$load FSC_H2O = FSC_H2O.l, FSC_O2 = FSC_O2.l
$load TFSC_CO2e = TFSC_CO2e.l, TFSC_CO2p = TFSC_CO2p.l, TFSC_CO2c = TFSC_CO2c.l, TFSC_CO2 = TFSC_CO2.l
$load FOM_coal, VOM_coal, FSC_coal_prov, FSC_cwater_prov, FSC_eC_prov
$load FOM_Msyn_prov, VOM_Msyn_prov
$load DOI_prov
$load MeOH_Cap_prov
$load FSC_CO2e_city_woi
$load  DLCOR, RLCCE
$gdxin

* ---------------- PV and WT ------------------------* 
Parameter PV_prov(j), WT_prov(j), PV, WT;
Parameter PV_CAP, PV_OM, WT_CAP, WT_OM;
PV_prov(j) = sum(ix, Capex_RE('PV',j,ix)) + sum(ix, FOM_RE('PV',j,ix));
WT_prov(j) = sum(ix, Capex_RE('WT',j,ix)) + sum(ix, FOM_RE('WT',j,ix));
PV = sum(j, PV_prov(j));
WT = sum(j, WT_prov(j));

PV_CAP = sum((j,ix),Capex_RE('PV',j,ix));
PV_OM = sum((j,ix),FOM_RE('PV',j,ix));

WT_CAP = sum((j,ix),Capex_RE('WT',j,ix));
WT_OM = sum((j,ix),FOM_RE('WT',j,ix));

Display PV_prov, WT_prov, PV, WT
Display PV_CAP, PV_OM, WT_CAP, WT_OM

* -------------------- EL ----------------------------*
Parameter EL_prov(j), EL, EL_CAP, EL_OM;
EL_prov(j) = sum(i,(Capex_EL(j,i) + FOM_EL(j,i) + VOM_EL(j,i)));
EL = sum(j, EL_prov(j));

EL_CAP = sum((j,i),Capex_EL(j,i));
EL_OM = sum((j,i), (FOM_EL(j,i)+VOM_EL(j,i)));


Display EL_prov, EL, EL_CAP, EL_OM


* ---------------------Lib---------------------------*
Parameter Lib_prov(j), Lib, Lib_CAP, Lib_OM;
Lib_prov(j) = sum(i,(Capex_ES('Lib',j,i) + FOM_ES('Lib',j,i) + VOM_ES('Lib',j,i)));
Lib = sum(j, Lib_prov(j));

Lib_CAP = sum((j,i),(Capex_ES('Lib',j,i)));
Lib_OM = sum((j,i),(FOM_ES('Lib',j,i) + VOM_ES('Lib',j,i)));


Display Lib_prov, Lib, Lib_CAP, Lib_OM

* ---------------------Storage tank---------------------------*
Parameter %TN%_CAP, %TN%_OM;


%TN%_CAP = sum((j,i),(Capex_ES('%TN%',j,i)));
%TN%_OM = sum((j,i),(FOM_ES('%TN%',j,i) + VOM_ES('%TN%',j,i)));


Display %TN%_CAP, %TN%_OM



* --------------------- Grid ---------------------------*
Parameter Grid_prov(j), Grid;
Grid_prov(j) = sum((i),E_purs(j,i));
Grid = sum(j, Grid_prov(j));
Display Grid_prov, Grid

* -------------------H2O, O2, CO2 -------------------------*
Parameter H2O_prov(j), H2O;
H2O_prov(j) = sum((i),FSC_H2O(j,i));
H2O = sum(j, H2O_prov(j));
Display H2O_prov, H2O

Parameter O2_prov(j), O2;
O2_prov(j) = sum((i),FSC_O2(j,i));
O2 = sum(j, O2_prov(j));
Display O2_prov, O2


Parameter TCO2e, TCO2p, TCO2c, TCO2;
TCO2e = sum(j,TFSC_CO2e(j));
TCO2p = sum(j,TFSC_CO2p(j));
TCO2c = sum(j,TFSC_CO2c(j));
TCO2 = sum(j,TFSC_CO2(j));

* ---------------------Integrated Coal processing ------------------------------*
Parameter OM_coal_prov(j), OM_coal, coal_pur_prov(j), coal_pur;
OM_coal_prov(j) = FOM_coal(j) + VOM_coal(j);
OM_coal = sum(j, OM_coal_prov(j)* (1- DOI_prov(j)));

coal_pur_prov(j) = FSC_coal_prov(j) * (1- DOI_prov(j));
coal_pur = sum(j, coal_pur_prov(j));
Display OM_coal_prov, OM_coal, coal_pur_prov, coal_pur

* ---------------------Msyn processing ------------------------------*
Parameter OM_Msyn_prov(j), OM_Msyn;
OM_Msyn_prov(j) = FOM_Msyn_prov(j) + VOM_Msyn_prov(j);
OM_Msyn = sum(j, OM_Msyn_prov(j));

* ----------------------Define all_data-------------------------------*


Parameter Eco_cost(cbd);
Eco_cost('PV_CAP') = PV_CAP;
Eco_cost('PV_OM') = PV_OM;

Eco_cost('WT_CAP') = WT_CAP;
Eco_cost('WT_OM') = WT_OM;

Eco_cost('%EL%_CAP') = EL_CAP;
Eco_cost('%EL%_OM') = EL_OM;

Eco_cost('Lib_CAP') = Lib_CAP;
Eco_cost('Lib_OM') = Lib_OM;

Eco_cost('%TN%_CAP') = %TN%_CAP;
Eco_cost('%TN%_OM') = %TN%_OM;


Eco_cost('TNS') = 0;
Eco_cost('Grid') = Grid;
Eco_cost('H2O') = H2O;
Eco_cost('O2') = -O2;
Eco_cost('CO2e') = TCO2e;
Eco_cost('CO2p') = TCO2p;
Eco_cost('CO2c') = TCO2c;
Eco_cost('OM_coal') = OM_coal;
Eco_cost('Coal') = coal_pur;
Eco_cost('OM_Msyn') = OM_Msyn;
Parameter Eco_cost_LCOM(cbd);

Eco_cost_LCOM(cbd) = Eco_cost(cbd) / (sum(j, MeOH_Cap_prov(j)));

display Eco_cost_LCOM


* ==================BAU Coal processing ==========================================*
Parameter OM_coal_prov_woi(j), OM_coal_woi, coal_pur_prov_woi(j), coal_pur_woi;
OM_coal_prov_woi(j) = FOM_coal(j) + VOM_coal(j);
OM_coal_woi = sum(j, OM_coal_prov_woi(j));

coal_pur_prov_woi(j) = FSC_coal_prov(j);
coal_pur_woi = sum(j, coal_pur_prov_woi(j));
Display OM_coal_prov_woi, OM_coal_woi, coal_pur_prov_woi, coal_pur_woi

Parameter FSC_eC_woi, FSC_cwater_woi, FSC_CO2e_woi ;
FSC_eC_woi = sum(j, FSC_eC_prov(j));
FSC_cwater_woi = sum(j, FSC_cwater_prov(j));
FSC_CO2e_woi = sum((j,i),FSC_CO2e_city_woi(j,i));

Set cbau  /OM_coal, Coal, Grid, H2O, CO2, OM_Msyn/;
Parameter Eco_cost_BAU(cbau);
Eco_cost_BAU('OM_coal') = OM_coal_woi;
Eco_cost_BAU('Coal') = coal_pur_woi;
Eco_cost_BAU('Grid') = FSC_eC_woi;
Eco_cost_BAU('H2O') = FSC_cwater_woi;
Eco_cost_BAU('CO2') = FSC_CO2e_woi;
Eco_cost_BAU('OM_Msyn') = OM_Msyn;

Display Eco_cost_BAU

* ------------------Write in Excel -------------------*

Execute_Unload 'BAU_%EL%_%YR%.gdx' Eco_cost_BAU;
$onEcho > Eco_cost_BAU.txt
Text = "Type"                rng = Eco_cost_BAU!A1
Text = "Value"               rng = Eco_cost_BAU!B1
Par = Eco_cost_BAU               rng = Eco_cost_BAU!A2      rDim = 1
$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw BAU_%EL%_%YR%.gdx output = %Bfolder%BAU_%EL%_%YR%.xlsx @Eco_cost_BAU.txt';

*==========================CO2 BREAKDOWN====================================*
Set yr / 2030, 2040, 2050 /;

Scalar PV_CO2  Carbon emission factor throughout full life cyc of PV [tonne per MWh] / 0.0142 /
       WT_CO2  Carbon emission factor throughout full life cyc of PV [tonne per MWh] / 0.01 / 
       CO2CtM   Carbon emission for each tone of methanol produced [tco2 per tonne] / 4.368 /;

Parameters P_PV(j,ix,h), RLCCE_PV_prov(j)
           P_WT(j,ix,h), RLCCE_WT_prov(j)
           P_grid(j,i,h), RLCCE_grid_prov(j)
           M_EL(csp,j,i,h), M_RWS(csp,j,i,h), RLCCE_React_prov(j)
           CO2_em(j,i,h), CF_CO2(j,yr);

$call csv2gdx %Dfolder%CEF_grid.csv  id = CF_CO2  index = 1  values = 2..lastCol  useHeader = y
$gdxin CEF_grid.gdx
$load CF_CO2
$gdxin
        
$gdxin %Sfolder%%TP%_%EL%_%YR%_%ED%.gdx
$load P_PV = P_PV.l, P_WT = P_WT.l, P_grid = P_grid.l, M_EL = M_EL.l, CO2_em = CO2_em.l
$gdxin

RLCCE_PV_prov(j) = sum((ix,h), nds * P_PV(j,ix,h) * PV_CO2);
RLCCE_WT_prov(j) = sum((ix,h), nds * P_WT(j,ix,h) * WT_CO2);
RLCCE_grid_prov(j) = sum((i,h), nds * CF_CO2(j,'%YR%') * P_grid(j,i,h));
RLCCE_React_prov(j) = -sum((i,h), nds * (M_EL('CO2',j,i,h) ));

Display RLCCE_PV_prov, RLCCE_WT_prov, RLCCE_grid_prov, RLCCE_React_prov

Parameters  CO2_PV, CO2_WT, CO2_grid, CO2_cons;

CO2_PV = sum(j, RLCCE_PV_prov(j));
CO2_WT = sum(j, RLCCE_WT_prov(j));
CO2_grid = sum(j, RLCCE_grid_prov(j));
CO2_cons = sum(j, RLCCE_React_prov(j));

Display CO2_PV, CO2_WT, CO2_grid, CO2_cons

sets cc / PV, WT, Grid, Electrification, Coal/;

Parameter CO2_cost(cc);
CO2_cost('PV') = CO2_PV / (sum(j, MeOH_Cap_prov(j) * ths * DOI_prov(j)));
CO2_cost('WT') = CO2_WT / (sum(j, MeOH_Cap_prov(j) * ths * DOI_prov(j)));
CO2_cost('Grid') = CO2_grid / (sum(j, MeOH_Cap_prov(j) * ths * DOI_prov(j)));
CO2_cost('Electrification') = CO2_cons / (sum(j, MeOH_Cap_prov(j) * ths * DOI_prov(j)));
CO2_cost('Coal') = CO2CtM * (1 - %DOI%);

Display CO2_cost;

* =======================Decarbonization cost=================================*
Parameter Decar_cost;

Decar_cost = DLCOR / MAX(0.001, (CO2CtM - RLCCE)) ;
*Decar_cost = RLCCE;
Display Decar_cost
* ------------------Write in Excel -------------------*
Execute_Unload 'All_data_%EL%_%YR%_%ED%.gdx' Eco_cost, CO2_cost, Decar_cost;
$onEcho > Eco_cost.txt
Text = "Type"                rng = Eco_cost!A1
Text = "Value"               rng = Eco_cost!B1
Par = Eco_cost               rng = Eco_cost!A2      rDim = 1

Text = "Type"                rng = CO2_contribution!A1
Text = "Value"               rng = CO2_contribution!B1
Par = CO2_cost               rng = CO2_contribution!A2      rDim = 1

Text = "Decarbonization cost"   rng = Decarbonization!A1
Par = Decar_cost     rng = Decarbonization!B1

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw All_data_%EL%_%YR%_%ED%.gdx output = %Cfolder%TCB_UE_CAP_%TP%_%EL%_%YR%_%ED%.xlsx @Eco_cost.txt';

