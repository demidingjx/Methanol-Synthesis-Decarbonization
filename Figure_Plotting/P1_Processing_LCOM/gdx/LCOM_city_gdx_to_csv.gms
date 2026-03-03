
$Title Processing relevant gdx to csv

$eolCom //
$Set ED  ED25
$Set EL  PEM
$Set Disk E
$Set folder GDX7_M12_Fix

$Set tl  288
$Set rs  288
$Set el  PEM
$Set ys  2030           //year
$Set yl  5              //interest rate
$Set doi 0.50          //ed
$Set Scn BLN       //BLN, CN60
$Set TNS 0.30      //Transmission capacity
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
     res(j,ix)        Renewable energy generation in city ix in province j    
     cpv(j,ix)        Solar PV generation in city ix province j
     cwd(j,ix)        Onshore wind generation in city ix province j
     imz(j,ix,i)      possile line connections from city ix to i in province j
     rmz(j,irx,i)     possible line connections from city irx (no MeOH plt) to i in province j
     mmz(j,iim,i)     possible line connections from cit iim (have MeOH plt) to i (another MeOH plt)in procinve j
     umz(j,iim,i)     One direction line connections from cit iim (have MeOH plt) to i (another MeOH plt)in procinve j;
     

Sets rg(g)   Renewable energy generation technology   / PV, WT /
     es(g)   Energy storage technology                / LiB, HST /;

Parameter
    Capex_RE(rg,j,ix), FOM_RE(rg,j,ix)
    Capex_EL(j,i), FOM_EL(j,i), VOM_EL(j,i)
    Capex_RWS(j,i), FOM_RWS(j,i), VOM_RWS(j,i)
    Capex_ES(es,j,i), FOM_ES(es,j,i), VOM_ES(es,j,i)
    E_purs(j,i), FSC_H2O(j,i), FSC_O2(j,i), FSC_CO2p(j,i), FSC_CO2c(j,i), FSC_CO2e(j,i)
    DoI_city(j,i), FOM_coal_city(j,i), FSC_cwater_city(j,i), FSC_eC_city(j,i)
    FSC_coal_city(j,i);

$gdxin %Sfolder_2030%C_%EL%_2030_%ED%.gdx
$load Capex_RE = Capex_RE.l, FOM_RE = FOM_RE.l
$load Capex_EL = Capex_EL.l, FOM_EL = FOM_EL.l, VOM_EL = VOM_EL.l
$load Capex_RWS = Capex_RWS.l, FOM_RWS = FOM_RWS.l, VOM_RWS = VOM_RWS.l
$load Capex_ES = Capex_ES.l, FOM_ES = FOM_ES.l, VOM_ES = VOM_ES.l
$load E_purs = E_purs.l
$load FSC_H2O = FSC_H2O.l, FSC_O2 = FSC_O2.l, FSC_CO2p = FSC_CO2p.l, FSC_CO2c = FSC_CO2c.l, FSC_CO2e = FSC_CO2e.l
$load DoI_city = DoI_city.l, FOM_coal_city = FOM_coal_city.l, FSC_cwater_city = FSC_cwater_city.l, FSC_eC_city = FSC_eC_city.l
$load FSC_coal_city = FSC_coal_city.l


Scalars Coal_FOM        Reference FOM of coal-syngas generating / 377 /
        Coal_VOM        Reference VOM of coal-syngas generating / 0.0257 /
        CtM             Reference coal-to-methanol ratio / 1.25837 / //1.25837
        CtMW            Reference coal-to-methanol water requirement / 4.23 / //1.53715 - 用LCWC替代
        ECtM            Electricity consumption for each tone of in the coal-based routine [MWh per tonne] / 1.731951 /;


Scalars Msyn_FOM   Reference FOM of methanol synthesis and distillating / 23.6 /    //$k/(ton/hr)/yr
        Msyn_VOM   Reference VOM of coal-syngas generating    / 0.003 /  //$k/ton 
        EStM       Electricity consumption for each tone of in the synthesis [MWh per tonne] / 1.254 /;
        
Parameters FOM_Msyn_city(j,i), VOM_Msyn_city(j,i), TAC_Msyn_city(j,i), FSC_eM_city(j,i);

FOM_Msyn_city(j,i) = MeOH_Cap_hr(j,i) * Msyn_FOM;

Display FOM_Msyn_city;
FSC_eM_city(j,i) = sum(h, MeOH_Cap_hr(j,i) * ECtM * tou(j,h) * %TOU% **(%yl%)); //k$

VOM_Msyn_city(j,i) = FSC_eM_city(j,i) + MeOH_Cap_yr(j,i) * ths * Msyn_VOM;

TAC_Msyn_city(j,i) = FOM_Msyn_city(j,i) + VOM_Msyn_city(j,i);


Parameters VOM_coal_city(j,i), LCOM_city(j,ix);

VOM_coal_city(j,i) = MeOH_Cap_yr(j,i) * ths * Coal_VOM ;

LCOM_city(j,i) = sum(rg, Capex_RE(rg,j,i)) + Capex_EL(j,i) + Capex_RWS(j,i) + sum(es, Capex_ES(es,j,i))
                  + sum(rg, Fom_RE(rg,j,i)) + FOM_EL(j,i) + FOM_RWS(j,i) + sum(es, FOM_ES(es,j,i))
                  + VOM_EL(j,i) + sum(es, VOM_ES(es,j,i)) + VOM_RWS(j,i)
                  + E_Purs(j,i) + FSC_H2O(j,i) + FSC_CO2e(j,i) + FSC_CO2p(j,i) + FSC_CO2c(j,i) - FSC_O2(j,i)
                  +(1 - DoI_city(j,i)) * (FOM_coal_city(j,i) + FSC_cwater_city(j,i) + FSC_eC_city(j,i) + VOM_coal_city(j,i) + FSC_coal_city(j,i))
                  + TAC_Msyn_city(j,i);



$onEcho > howToWrite_C_2030.txt

Text = "City_LCOM"           rng = 2030_LCOM!A5
Par = LCOM.l                 rng = 2030_LCOM!B5 
Text = "City_RLCCE"           rng = 2030_RLCCE!A4
Par = RLCCE.l                rng = 2030_RLCCE!B4 

Text = "City_LCOM_j"          rng = 2030_City_RLCCE_j!A1
Text = "Value"                rng = 2030_City_RLCCE_j!B1 
Par = RLCCE_prov               rng = 2030_City_RLCCE_j!A2     rDim = 1

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw %Sfolder_2030%C_%EL%_2030_%ED%.gdx output = %Lfolder%LCOM_city_%ys%_%EL%_%ED%.xlsx.xlsx @howToWrite_C_2030.txt';


Execute_Unload 'LCOM_city_%EL%_%YR%.gdx' LCOM_city;
$onEcho > LCOM_city_2030.txt
Text = "City_LCOM_j"          rng = 2030_City_LCOM_j!A1
Text = "Value"                rng = 2030_City_LCOM_j!B1 
Par = LCOM_city               rng = 2030_City_LCOM_j!A2     rDim = 2
$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw LCOM_city_%EL%_%YR%.gdx output = %Lfolder%LCOM_city_%ys%_%EL%_%ED%.xlsx @LCOM_city_2030.txt';




