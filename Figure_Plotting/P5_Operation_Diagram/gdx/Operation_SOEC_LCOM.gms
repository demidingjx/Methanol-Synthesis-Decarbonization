$eolCom //
$Set EL  SOE    
$Set TN  SST
$Set rs  288
$Set ys  2040
$Set yl  15              //interest rate
$Set ED  ED25
$Set DOI 0.25
$Set Disk E
$Set folder GDX7_M12_Fix
$Set TNS 0.30      //Transmission capacity
$Set TOU 1.02249   //Electricity price
$Set Scn BLN       //BLN, CN60


Set      yr     / 2025, 2030, 2040, 2050 /
         g      / PV, WT, PEM, SOE, LiB, HST, SST, RWS, MSR /;
Set     yre(yr) / %ys% /;                                 // years for cost calculation


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


*输入gdx文件 - Define the gdx file path (GDX1_M12,记得改年份)
$Set Sfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\%folder%\%EL%\%ys%\%ED%\

*输出excel文件 - Define the output excel location (LCOM，年份)
$Set Cfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\P5_Operation_Diagram\Excel\

*相关Data
$Set Dfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\csv_Single_Prov\

Parameter         Tech_VOM(g,yr)      Parameter of economic factors VOM   // kUSD/MWh,   kUSD/ton

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

Sets irx(ix)  citis without methanol synthesis plants;
$call csv2gdx %Dfolder%Cities_wo_MeOH.csv  id = irx  index = 1  useHeader = y 
$gdxIn Cities_wo_MeOH.gdx
$load irx
$gdxin

$call csv2gdx %Dfolder%VOM.csv  id = Tech_VOM  index = 1  values = 2..lastCol  useHeader = y
$gdxin VOM.gdx
$load Tech_VOM
$gdxin

* ===== Methaol plants ===== *
Parameter MeOH_Cap_yr(j,i), MeOH_Cap_hr(j,i);   // Caps of methanol plant i in province j [ktonne]
$call csv2gdx %Dfolder%MeOH_Caps.csv  id = MeOH_Cap_yr  index = 1,2  values = 3..lastCol  useHeader = y
$gdxin MeOH_Caps.gdx
$load MeOH_Cap_yr
$gdxin

MeOH_Cap_hr(j,i) = MeOH_Cap_yr(j,i) * ths / nhs;   // kton/yr convert to tonne/hr

Display MeOH_Cap_yr, MeOH_Cap_hr;


Alias (j,jx);    // Provinces
Alias (i,iim);   // iim, cities with methanol plants

Display j, ix, irx, i, iim;

alias (js,j);
Alias (jsx,js);

* ======Distance between city and city ======*
Parameters cDstn(j,ix,i);   // Distance between city ix and i with methanol plants in province j [km]
$call csv2gdx %Dfolder%Prefecture_Distance.csv  id = cDstn  index = 1,2  values = 3..lastCol  useHeader = y
$gdxin Prefecture_Distance.gdx
$load cDstn
$gdxin

Display cDstn;

* ========Capacity of grid capacity betwen Prov and Prov ===== *
Parameters U_prov_nom(ln,js,j);
           // 117.90 (China’s Thermal Coal;   // Distance between prov j and jx [km]
$call csv2gdx %Dfolder%TNS_caps.csv  id = U_prov_nom  index = 1,2,3  values = 4..lastCol  useHeader = y
$gdxin TNS_caps.gdx
$load U_prov_nom
$gdxin

Parameters
        uCO2e(yr)           Reference CO2 emision price [$ per tonne]  // 11.62
        uCO2c(yr)           Reference CO2 capture price based on coal-based [$ per tonne]
        uCO2p(yr)           Reference CO2 purchase price [$ per tonne]
        uCoal(yr)           Reference coal price [$ per tonne]
        CF_CO2(j,yr)        Carbon emission factor for each province [tonne CO2 per MWh ]
        tou(j,h);
$call csv2gdx %Dfolder%Electricity_%rs%.csv  id = tou  index = 1  values = 2..lastCol  useHeader = y
$gdxin Electricity_%rs%.gdx
$load tou
$gdxin

$call csv2gdx %Dfolder%CO2c.csv  id = uCO2c  index = 1  values = 2..lastCol  useHeader = y
$gdxin CO2c.gdx
$load uCO2c
$gdxin

$call csv2gdx %Dfolder%CO2e_%Scn%.csv  id = uCO2e  index = 1  values = 2..lastCol  useHeader = y
$gdxin CO2e_%Scn%.gdx
$load uCO2e
$gdxin

$call csv2gdx %Dfolder%CO2p.csv  id = uCO2p  index = 1  values = 2..lastCol  useHeader = y
$gdxin CO2p.gdx
$load uCO2p
$gdxin

$call csv2gdx %Dfolder%Coal_price.csv  id = uCoal  index = 1  values = 2..lastCol  useHeader = y
$gdxin Coal_price.gdx
$load uCoal
$gdxin

$call csv2gdx %Dfolder%CEF_grid.csv  id = CF_CO2  index = 1  values = 2..lastCol  useHeader = y
$gdxin CEF_grid.gdx
$load CF_CO2
$gdxin

Parameters U_AC_nom(js,j), U_DC_nom(js,j);

U_AC_nom(js,j) = U_prov_nom('AC',js,j);
U_DC_nom(js,j) = U_prov_nom('DC',js,j);

Display U_prov_nom, U_AC_nom, U_DC_nom;


Sets plt(j,i)         Methanol synthesis plant i in province j
     imz(j,ix,i)      possile line connections from city ix to i in province j
     rmz(j,irx,i)     possible line connections from city irx (no MeOH plt) to i in province j
     mmz(j,iim,i)     possible line connections from cit iim (have MeOH plt) to i (another MeOH plt)in procinve j
     umz(j,iim,i)     One direction line connections from cit iim (have MeOH plt) to i (another MeOH plt)in procinve j
     emz(ln,jx,j)     possible line connections between province jx and j
     vmz(ln,jx,j)     Possible power flow from jx to j;
     
plt(j,i)$(MeOH_Cap_yr(j,i)) = yes;                           // Methanol synthesis plant in province j
imz(j,ix,i)$(cDstn(j,ix,i)) = yes;                           // Possible power flows between city ix and i in province j
mmz(j,iim,i)$(cDstn(j,iim,i)) = yes;                         // Possible power flows between city iim and i in province j
rmz(j,irx,i)$(cDstn(j,irx,i)) = yes;                         // Possible power flows from city irx to i in province j
umz(j,iim,i)$(cDstn(j,iim,i) and ord(iim) < ord(i)) = yes;   // Possible line connection between city iim and i
emz(ln,js,j)$(U_prov_nom(ln,js,j)) = yes;                    // Possible line connection between province jx and j
vmz(ln,js,j)$(U_prov_nom(ln,js,j)) = yes;
vmz(ln,j,js)$(U_prov_nom(ln,js,j)) = yes;


*---------------------读数据----------------------------*
Parameter U_nom(j,ix,cb), P_PV(j,ix,h), P_WT(j,ix,h), P_EL(j,i,h), ChgP(es,j,i,h), DisP(es,j,i,h), 
          P_grid(j,i,h), MeOH_coal_hr(j,i,h), M_MSR(csp,j,i,h), En_ES(es,j,i,h)
          M_EL(csp,j,i,h);

$gdxin %Sfolder%S_%EL%_%ys%_%ED%.gdx
$load U_nom = U_nom.l, P_PV = P_PV.l, P_WT = P_WT.l, P_EL = P_EL.l, ChgP = ChgP.l, DisP = DisP.l, P_grid = P_grid.l, MeOH_coal_hr = MeOH_coal_hr.l, M_EL = M_EL.l,  M_MSR = M_MSR.l, En_ES = En_ES.l
$gdxin

Display P_PV, P_WT, P_EL, ChgP, DisP, P_grid, MeOH_coal_hr, M_MSR, En_ES

Parameter Tol_P_PV(h), Tol_P_WT(h), Tol_P_EL(h), Tol_ChgP_LiB(h), Tol_DisP_LiB(h), Tol_ChgP_tank(h),
          Tol_DisP_tank(h), Tol_P_grid(h), Tol_MeOH_coal_hr(h), Tol_M_MSR(h), Tol_En_ES_LiB(h), Tol_En_ES_tank(h);

Tol_P_PV(h) = sum((j,ix),P_PV(j,ix,h)) * 10E-3; //GWH
Tol_P_WT(h) = sum((j,ix),P_WT(j,ix,h)) * 10E-3;
Tol_P_EL(h) = sum((j,i),P_EL(j,i,h)) * 10E-3;
Tol_ChgP_LiB(h) = sum((j,i),ChgP('LiB',j,i,h)) * 10E-3;
Tol_DisP_LiB(h) = sum((j,i),DisP('LiB',j,i,h)) * 10E-3;
Tol_ChgP_tank(h) = sum((j,i),ChgP('%TN%',j,i,h)) * 0.00594; 
Tol_DisP_tank(h) = sum((j,i),DisP('%TN%',j,i,h)) * 0.00594;
Tol_En_ES_LiB(h) = sum((j,i),En_ES('LiB',j,i,h)) * 10E-3;
Tol_En_ES_tank(h) = sum((j,i),En_ES('%TN%',j,i,h)) * 0.00594;
Tol_P_grid(h) = sum((j,i),P_grid(j,i,h)) * 10E-3;
Tol_MeOH_coal_hr(h) = sum((j,i),MeOH_coal_hr(j,i,h)) * 5.8611 * 10E-3 ; //21.1 MJ/kg *1000 /3.6e6
Tol_M_MSR(h) = sum((j,i),M_MSR('MeOH',j,i,h)) * 5.8611 * 10E-3 ; //21.1 MJ/kg *1000 /3.6e6
Display Tol_P_PV, Tol_P_WT, Tol_P_EL, Tol_ChgP_LiB, Tol_DisP_LiB, Tol_ChgP_tank, Tol_DisP_tank, Tol_En_ES_LiB, Tol_En_ES_tank, Tol_P_grid, Tol_MeOH_coal_hr, Tol_M_MSR;




*==============LCOM==================================*
Parameter
    Capex_RE(rg,j,ix), FOM_RE(rg,j,ix)
    Capex_EL(j,i), FOM_EL(j,i), VOM_EL(j,i)
    Capex_ES(es,j,i), FOM_ES(es,j,i), VOM_ES(es,j,i)
    VOM_Pcity(j,ix,i), VOM_Pprov(ln,js,j)
    E_purs(j,i), FSC_H2O(j,i), FSC_O2(j,i), FSC_CO2(j,i)
    TFSC_CO2e(j), TFSC_CO2p(j), TFSC_CO2c(j), TFSC_CO2(j)
    FSC_cwater_prov(j), FSC_eC_prov(j)
    FOM_coal(j), VOM_coal(j), FSC_coal_prov(j)
    Capex(j), FOM(j)
    FOM_Msyn_prov(j), VOM_Msyn_prov(j)
    P_city(j,ix,i,h), F_prov(ln,js,j,h)
    DOI_prov(j), DOI
    MeOH_Cap_prov(j)
    FSC_CO2e_city_woi(j,i)
    DLCOR, RLCCE
    CO2_capt(js,i,h), CO2_pur(js,i,h), CO2_em(js,i,h);

$gdxin %Sfolder%S_%EL%_%ys%_%ED%.gdx
$load Capex_RE = Capex_RE.l, FOM_RE = FOM_RE.l
$load Capex_EL = Capex_EL.l, FOM_EL = FOM_EL.l, VOM_EL = VOM_EL.l
$load Capex_ES = Capex_ES.l, FOM_ES = FOM_ES.l, VOM_ES = VOM_ES.l
$load Capex = Capex.l, FOM = FOM.l
$load VOM_Pcity = VOM_Pcity.l, VOM_Pprov = VOM_Pprov.l,
$load E_purs = E_purs.l
$load FSC_H2O = FSC_H2O.l, FSC_O2 = FSC_O2.l
$load TFSC_CO2e = TFSC_CO2e.l, TFSC_CO2p = TFSC_CO2p.l, TFSC_CO2c = TFSC_CO2c.l, TFSC_CO2 = TFSC_CO2.l
$load FOM_coal, VOM_coal, FSC_coal_prov, FSC_cwater_prov, FSC_eC_prov
$load FOM_Msyn_prov, VOM_Msyn_prov
$load P_city = P_city.l, F_prov  = F_prov.l
$load DOI_prov
$load MeOH_Cap_prov
$load FSC_CO2e_city_woi
$load DLCOR, RLCCE
$load CO2_capt = CO2_capt.l, CO2_pur = CO2_pur.l, CO2_em = CO2_em.l
$gdxin

Display CO2_capt, CO2_pur, CO2_em

Scalars ir         interst rate                       / 0.05 /
        uH2O       water cost [$ per tonne]           / 0.362 /
        uO2        O2 COST [$ per tonne]              / 63.57 /
        City_VOM   Electricity TNS cost between cities within province [USD per MWh] / 0.169 /
        Coal_VOM        Reference VOM of coal-syngas generating / 0.0257 /
        CtM             Reference coal-to-methanol ratio / 1.25837 / //1.25837
        CtMW            Reference coal-to-methanol water requirement / 4.23 / //1.53715 - 用LCWC替代
        ECtM            Electricity consumption for each tone of in the coal-based routine [MWh per tonne] / 1.731951 /
        Msyn_FOM   Reference FOM of methanol synthesis and distillating / 23.6 /    //$k/(ton/hr)/yr
        Msyn_VOM   Reference VOM of coal-syngas generating    / 0.003 /  //$k/ton 
        EStM       Electricity consumption for each tone of in the synthesis [MWh per tonne] / 1.254 /;
        
Parameters  CRF(g)
            Prov_VOM(ln)   Electricity TNS cost between provinces [USD per MWh] / AC 5.37, DC 5.37 /;
        
Parameter Capex_t, Fom_t, VOM_h(h), VOM_city_h(h), VOM_Pprov_h(h), E_Purs_h(h)
          FSC_H2O_t(h), FSC_O2_t(h), FSC_CO2e_t(h), FSC_CO2p_t(h), FSC_CO2c_t(h)
          FOM_coal_t, VOM_coal_t(h), FSC_cwater_t(h), FSC_eC_t(h), FSC_coal_t(h)
          FOM_Msyn_prov_t, VOM_Msyn_prov_t(h), FSC_E_t(h);
          

Capex_t = sum(j, Capex(j))/8760; //kUSD/hr
Fom_t  = sum(j, FOM(j))/8760; //kUSD/hr
VOM_h(h) = sum((yre,js,i), Tech_VOM('%el%',yre) * P_EL(js,i,h))
         + sum((es,yre,js,i), (Tech_VOM('LiB',yre) * (ChgP('LiB',js,i,h) + DisP('LiB',js,i,h))))
         + sum((es,yre,js,i), (Tech_VOM('%TN%',yre) *  (ChgP('%TN%',js,i,h) + DisP('%TN%',js,i,h))))
         ; //kUSD/hr

VOM_city_h(h) = (sum((js,irx,i), City_VOM * (P_city(js,irx,i,h))) + sum((js,iim,i), City_VOM * (P_city(js,iim,i,h))))/ths;
VOM_Pprov_h(h) = (sum((ln,jsx,js), Prov_VOM(ln) * (F_prov(ln,jsx,js,h)))) / ths;
E_Purs_h(h) = sum((js,i), tou(js,h) * %TOU% **(%yl%) * P_grid(js,i,h));


FSC_H2O_t(h) = (uH2O * sum((js,i), (M_EL('H2O',js,i,h)))) / ths;
FSC_O2_t(h) = (uO2 * sum((js,i), M_EL('O2',js,i,h))) / ths;

FSC_CO2e_t(h) = (sum(yre, uCO2e(yre)) * sum((js,i),  CO2_em(js,i,h)))/ths;
FSC_CO2p_t(h) = (sum(yre, uCO2p(yre)) * sum((js,i),  CO2_pur(js,i,h)))/ths;
FSC_CO2c_t(h) = (sum(yre, uCO2c(yre)) * sum((js,i),  CO2_capt(js,i,h)))/ths;

FOM_coal_t = (sum(j, FOM_coal(j))/8760) * (1-%DOI%); //kUSD/hr
VOM_coal_t(h) = sum((j,i),MeOH_coal_hr(j,i,h)) * Coal_VOM; //kUSD/hr
FSC_cwater_t(h) = (sum((j,i),MeOH_coal_hr(j,i,h)) * CtMW * uH2O) / ths;  //kUSD/hr
FSC_eC_t(h) = sum(j, FSC_eC_prov(j)/8760);  //kUSD/hr
FSC_coal_t(h) = sum((yre,j,i), MeOH_coal_hr(j,i,h) * CtM * uCoal(yre)) / ths; //kUSD/hr

FOM_Msyn_prov_t = sum((j), FOM_Msyn_prov(j))/8760;
VOM_Msyn_prov_t(h) = sum((j), VOM_Msyn_prov(j))/8760;


Parameter test;
 test = sum(h, FSC_eC_t(h));
 Display test

Display Capex_t, Fom_t, VOM_h, VOM_city_h, VOM_Pprov_h, E_Purs_h, FSC_H2O_t, FSC_O2_t, FSC_CO2e_t, FSC_CO2p_t, FSC_CO2c_t
Display FOM_coal_t, VOM_coal_t, FSC_cwater_t, FSC_eC_t, FSC_coal_t
Display FOM_Msyn_prov_t, VOM_Msyn_prov_t

Parameter LCOM_t(h);

LCOM_t(h) = (Capex_t + Fom_t + VOM_h(h) + VOM_city_h(h) + VOM_Pprov_h(h) + E_Purs_h(h)
            + FSC_H2O_t(h) - FSC_O2_t(h) + FSC_CO2e_t(h) + FSC_CO2p_t(h) + FSC_CO2c_t(h)
            + FOM_coal_t + VOM_coal_t(h) + FSC_cwater_t(h) + FSC_eC_t(h) + FSC_coal_t(h)
            + VOM_Msyn_prov_t(h) + FOM_Msyn_prov_t) * ths / (sum((j,i),M_MSR('MeOH',j,i,h)));
Display LCOM_t;



Execute_Unload 'Dynamic_%EL%_%ys%_%ED%.gdx' Tol_P_PV, Tol_P_WT, Tol_P_EL, Tol_ChgP_LiB,
                                            Tol_DisP_LiB, Tol_ChgP_tank, Tol_DisP_tank,
                                            Tol_En_ES_LiB, Tol_En_ES_tank, Tol_P_grid, Tol_MeOH_coal_hr, Tol_M_MSR
                                            LCOM_t;
$onEcho > Dynamicoperation_%el%.txt
Text = "Hour_PV"                rng = Hour_PV!A1
Text = "Value"                  rng = Hour_PV!B1
Par = Tol_P_PV                  rng = Hour_PV!A2      rDim = 1

Text = "Hour_WT"                rng = Hour_WT!A1
Text = "Value"                  rng = Hour_WT!B1
Par = Tol_P_WT                  rng = Hour_WT!A2      rDim = 1

Text = "Hour_Grid"              rng = Hour_Grid!A1
Text = "Value"                  rng = Hour_Grid!B1
Par = Tol_P_grid                rng = Hour_Grid!A2      rDim = 1

Text = "Hour_EL"                rng = Hour_EL!A1
Text = "Value"                  rng = Hour_EL!B1
Par = Tol_P_EL                  rng = Hour_EL!A2      rDim = 1

Text = "Hour_ChgP_LiB"                rng = Hour_ChgP_LiB!A1
Text = "Value"                        rng = Hour_ChgP_LiB!B1
Par = Tol_ChgP_LiB                    rng = Hour_ChgP_LiB!A2      rDim = 1

Text = "Hour_DisP_LiB"                rng = Hour_DisP_LiB!A1
Text = "Value"                        rng = Hour_DisP_LiB!B1
Par = Tol_DisP_LiB                    rng = Hour_DisP_LiB!A2      rDim = 1

Text = "Hour_ChgP_%TN%"                rng = Hour_ChgP_%TN%!A1
Text = "Value"                         rng = Hour_ChgP_%TN%!B1
Par = Tol_ChgP_tank                    rng = Hour_ChgP_%TN%!A2      rDim = 1

Text = "Hour_DisP_%TN%"                rng = Hour_DisP_%TN%!A1
Text = "Value"                         rng = Hour_DisP_%TN%!B1
Par = Tol_DisP_tank                    rng = Hour_DisP_%TN%!A2      rDim = 1

Text = "Hour_EN_LiB"                   rng = Hour_EN_LiB!A1
Text = "Value"                         rng = Hour_EN_LiB!B1
Par = Tol_En_ES_LiB                    rng = Hour_EN_LiB!A2      rDim = 1

Text = "Hour_EN_%TN%"               rng = Hour_EN_%TN%!A1
Text = "Value"                      rng = Hour_EN_%TN%!B1
Par = Tol_En_ES_tank                rng = Hour_EN_%TN%!A2      rDim = 1

Text = "MeOH_coal_hr"                       rng = MeOH_coal_hr!A1
Text = "Value"                          rng = MeOH_coal_hr!B1
Par = Tol_MeOH_coal_hr                         rng = MeOH_coal_hr!A2      rDim = 1

Text = "Hour_MeOH"                        rng = Hour_MeOH!A1
Text = "Value"                            rng = Hour_MeOH!B1
Par = Tol_M_MSR                    rng = Hour_MeOH!A2      rDim = 1

Text = "LCOM_Hr"                        rng = LCOM_Hr!A1
Text = "Value"                          rng = LCOM_Hr!B1
Par = LCOM_t                            rng = LCOM_Hr!A2      rDim = 1

$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw Dynamic_%EL%_%ys%_%ED%.gdx output = %Cfolder%Hourly_%EL%_%ys%_%ED%.xlsx @Dynamicoperation_%el%.txt';









