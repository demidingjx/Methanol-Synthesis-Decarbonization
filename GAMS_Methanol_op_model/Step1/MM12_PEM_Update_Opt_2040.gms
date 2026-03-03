$Title Accelerating green methanol production with spatial integration of electrolysis

$eolCom //

$Set tl  288
$Set rs  288
$Set el  PEM
$Set ys  2040           //year
$Set yl  15              //interest rate
$Set doi 1.0           //ed
$Set ED  100
$Set Scn BLN       //BLN, CN60
$Set TNS 0.30      //Transmission capacity
$Set TOU 1.02249   //Electricity price
//Set definition
Sets t      / h0 * h%tl% /
     h(t)   / h1 * h%tl% /
     co     / a, b /
     csp    / H2, O2, H2O, CO2, Gas, MeOH /
     g      / PV, WT, PEM, SOE, LiB, HST, SST, RWS, MSR /
     sp     / eta, ro, lm, cfn, cfm, mn, ltm /
     eco    / CAPEX, FOM, VOM /
     yr     / 2025, 2030, 2040, 2050 /
     ln     / AC, DC /;
     
Scalars  nhs   number hours in a year    / 8760 /
         ths   thousand                 / 1.0e+3 /
         mms   million                  / 1.0e+6 /
         nds   number of typical days;

nds = nhs / %tl%;

$Set Dfolder /dssg/home/acct-zmliu/zmliu/Jiaxin_Ding_Conference_MeOH/Data/
$Set Sfolder /dssg/home/acct-zmliu/zmliu/Jiaxin_Ding_Conference_MeOH/Data/288_Re_run/
//$Set Gfolder /dssg/home/acct-zmliu/jiaxin.ding/2025_Jiaxin_Ding/Data/288_gdx/%el%/

$ontext
$Set Dfolder F:\2025_Methanol_synthesis\3_GAMS\csv_Single_Prov\
$Set Sfolder F:\2025_Methanol_synthesis\3_GAMS\csv_Single_Prov\test\
$Set Gfolder F:\2025_Methanol_synthesis\3_GAMS\csv_Single_Prov\288_gdx\%el%\
$offText
// Import data for system optimization      
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

Alias (j,jx);    // Provinces
Alias (i,iim);   // iim, cities with methanol plants

Display j, ix, irx, i, iim;

* ===== PV IMPORT ===== *
Parameter PV_Caps(j,ix), PV_CF(j,ix,h);

$call csv2gdx %Dfolder%Solar_PV_Capacity.csv  id = PV_Caps  index = 1,2  values = 3..lastCol  useHeader = y
$gdxIn Solar_PV_Capacity.gdx
$load PV_Caps
$gdxin

$call csv2gdx %Dfolder%Solar_PV_CF_%tl%.csv        id = PV_CF    index = 1,2  values = 3..lastCol  useHeader = y
$gdxIn Solar_PV_CF_%tl%.gdx
$load PV_CF
$gdxin

PV_CF(j,ix,h)$(PV_CF(j,ix,h) < 0.05) = 0.0;

* ===== WT IMPORT ===== *
Parameter OnWind_Caps(j,ix), OnWind_CF(j,ix,h);

$call csv2gdx %Dfolder%Onshore_Wind_Capacity.csv  id = OnWind_Caps  index = 1,2  values = 3..lastCol  useHeader = y
$gdxIn Onshore_Wind_Capacity.gdx
$load OnWind_Caps
$gdxin

$call csv2gdx %Dfolder%Onshore_Wind_CF_%tl%.csv        id = OnWind_CF    index = 1,2  values = 3..lastCol  useHeader = y
$gdxIn Onshore_Wind_CF_%tl%.gdx
$load OnWind_CF
$gdxin

OnWind_CF(j,ix,h)$(OnWind_CF(j,ix,h) < 0.05) = 0.0;

Display PV_Caps, PV_CF, OnWind_Caps, OnWind_CF;

* ===== Methaol plants ===== *
Parameter MeOH_Cap_yr(j,i), MeOH_Cap_hr(j,i);   // Caps of methanol plant i in province j [ktonne]
$call csv2gdx %Dfolder%MeOH_Caps.csv  id = MeOH_Cap_yr  index = 1,2  values = 3..lastCol  useHeader = y
$gdxin MeOH_Caps.gdx
$load MeOH_Cap_yr
$gdxin

MeOH_Cap_hr(j,i) = MeOH_Cap_yr(j,i) * ths / nhs;   // kton/yr convert to tonne/hr

Display MeOH_Cap_yr, MeOH_Cap_hr;

* =====Coefficients of surrogate models===== *
Parameters Coeff(g,csp,co);   // Coefficients of technologies from surrogate model
$call csv2gdx %Dfolder%SM_Param.csv  id = Coeff  index = 1,2  values = 3..lastCol  useHeader = y
$gdxin SM_Param.gdx
$load Coeff
$gdxin

Display Coeff;

* ===========Electricity price in each province ======= *
Parameters tou(j,h);
$call csv2gdx %Dfolder%Electricity_%tl%.csv  id = tou  index = 1  values = 2..lastCol  useHeader = y
$gdxin Electricity_%tl%.gdx
$load tou
$gdxin

* ======Distance between city and city ======*
Parameters cDstn(j,ix,i);   // Distance between city ix and i with methanol plants in province j [km]
$call csv2gdx %Dfolder%Prefecture_Distance.csv  id = cDstn  index = 1,2  values = 3..lastCol  useHeader = y
$gdxin Prefecture_Distance.gdx
$load cDstn
$gdxin

Display cDstn;

* ======Grid loss between Prov and Prov ======*
Parameters pln_loss(ln,jx,j);   // Distance between prov j and jx [km]
$call csv2gdx %Dfolder%TNS_loss.csv  id = pln_loss  index = 1,2,3  values = 4..lastCol  useHeader = y
$gdxin TNS_loss.gdx
$load pln_loss
$gdxin

pln_loss(ln,j,jx)$(pln_loss(ln,jx,j)) = pln_loss(ln,jx,j);

Display pln_loss;

* ========Capacity of grid capacity betwen Prov and Prov ===== *
Parameters U_prov_nom(ln,jx,j);   // Distance between prov j and jx [km]
$call csv2gdx %Dfolder%TNS_caps.csv  id = U_prov_nom  index = 1,2,3  values = 4..lastCol  useHeader = y
$gdxin TNS_caps.gdx
$load U_prov_nom
$gdxin

Parameters U_AC_nom(jx,j), U_DC_nom(jx,j);

U_AC_nom(jx,j) = U_prov_nom('AC',jx,j);
U_DC_nom(jx,j) = U_prov_nom('DC',jx,j);

Display U_prov_nom, U_AC_nom, U_DC_nom;

* =========Technological and Economic Parameters =======*
Parameters Param(g,sp)         Parameter for technologies
           Param_ltm(g,yr)     Parameter Lifetime for technologies
           Tech_CAP(g,yr)      Parameter of economic factors CAPEX  // kUSD/MW,    kUSD/ton/hr
           Tech_FOM(g,yr)      Parameter of economic factors FOM    // kUSD/MW/yr, kUSD/ton/yr
           Tech_VOM(g,yr)      Parameter of economic factors VOM   // kUSD/MWh,   kUSD/ton
           uCO2e(yr)           Reference CO2 emision price [$ per tonne]  // 11.62
           uCO2c(yr)           Reference CO2 capture price based on coal-based [$ per tonne]
           uCO2p(yr)           Reference CO2 purchase price [$ per tonne]
           uCoal(yr)           Reference coal price [$ per tonne] // 117.90 (China’s Thermal Coal Market)
           CF_CO2(j,yr)        Carbon emission factor for each province [tonne CO2 per MWh ]
           Eta_tech(g,yr)      Technology efficiency;

$call csv2gdx %Dfolder%Tech_Specs_MSR.csv  id = Param  index = 1  values = 2..lastCol  useHeader = y
$gdxin Tech_Specs_MSR.gdx
$load Param
$gdxin

$call csv2gdx %Dfolder%Lifetime.csv  id = Param_ltm  index = 1  values = 2..lastCol  useHeader = y
$gdxin Lifetime.gdx
$load Param_ltm
$gdxin

$call csv2gdx %Dfolder%CAPEX.csv  id = Tech_CAP  index = 1  values = 2..lastCol  useHeader = y
$gdxin CAPEX.gdx
$load Tech_CAP
$gdxin

$call csv2gdx %Dfolder%FOM.csv  id = Tech_FOM  index = 1  values = 2..lastCol  useHeader = y
$gdxin FOM.gdx
$load Tech_FOM
$gdxin

$call csv2gdx %Dfolder%VOM.csv  id = Tech_VOM  index = 1  values = 2..lastCol  useHeader = y
$gdxin VOM.gdx
$load Tech_VOM
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
       
$call csv2gdx %Dfolder%eta_tech.csv  id = Eta_tech  index = 1  values = 2..lastCol  useHeader = y
$gdxin eta_tech.gdx
$load Eta_tech
$gdxin
           
Display Param, Tech_CAP, Tech_FOM, Tech_VOM, uCO2e, uCoal, CF_CO2, Eta_tech;

* =================================Settings============================================ *
alias (js,j);
*Sets js(j)      / Ningxia /;   // Pronvice for testing
Sets yre(yr)    / %ys% /;                                 // years for cost calculation

Alias (jsx,js);

Sets plt(j,i)         Methanol synthesis plant i in province j
     res(j,ix)        Renewable energy generation in city ix in province j    
     cpv(j,ix)        Solar PV generation in city ix province j
     cwd(j,ix)        Onshore wind generation in city ix province j
     imz(j,ix,i)      possile line connections from city ix to i in province j
     rmz(j,irx,i)     possible line connections from city irx (no MeOH plt) to i in province j
     mmz(j,iim,i)     possible line connections from cit iim (have MeOH plt) to i (another MeOH plt)in procinve j
     umz(j,iim,i)     One direction line connections from cit iim (have MeOH plt) to i (another MeOH plt)in procinve j
     emz(ln,jx,j)     possible line connections between province jx and j
     vmz(ln,jx,j)     Possible power flow from jx to j;
     
plt(j,i)$(MeOH_Cap_yr(j,i)) = yes;                           // Methanol synthesis plant in province j
cpv(j,ix)$(PV_Caps(j,ix)) = yes;                             // PV generation in city ix in province j
cwd(j,ix)$(OnWind_Caps(j,ix)) = yes;                         // Wind generation in city ix in province j
res(j,ix)$(PV_Caps(j,ix) or OnWind_Caps(j,ix)) = yes;        // Renewable energy generation in city ix in province j

imz(j,ix,i)$(cDstn(j,ix,i)) = yes;                           // Possible power flows between city ix and i in province j
mmz(j,iim,i)$(cDstn(j,iim,i)) = yes;                         // Possible power flows between city iim and i in province j
rmz(j,irx,i)$(cDstn(j,irx,i)) = yes;                         // Possible power flows from city irx to i in province j
umz(j,iim,i)$(cDstn(j,iim,i) and ord(iim) < ord(i)) = yes;   // Possible line connection between city iim and i
emz(ln,jx,j)$(U_prov_nom(ln,jx,j)) = yes;                    // Possible line connection between province jx and j
vmz(ln,jx,j)$(U_prov_nom(ln,jx,j)) = yes;
vmz(ln,j,jx)$(U_prov_nom(ln,jx,j)) = yes;

Display plt, cpv, cwd, res, imz, mmz, rmz, umz, emz, vmz;

Sets rg(g)   Renewable energy generation technology   / PV, WT /
     es(g)   Energy storage technology                / LiB, HST /;

Parameters tau(g)    / LiB 4, HST 168 /;   // Storage duration

* ================================ Capacity sizing ================================ *
Positive variables U_RE_nom(g,j,ix)    Capacity of technology g installed in city ix (i) in province j;
Equations eqU_PV_nom, eqU_WT_nom;

* Solar and wind: Correct!
eqU_PV_nom(cpv(js,ix)) .. U_RE_nom('PV',js,ix) =L= PV_Caps(js,ix) * ths;       // MW, only for cities with PV caps
eqU_WT_nom(cwd(js,ix)) .. U_RE_nom('WT',js,ix) =L= OnWind_Caps(js,ix) * ths;   // MW, only for cities with WT caps

eqU_PV_nom.scale(cpv(js,ix)) = 100;
eqU_WT_nom.scale(cwd(js,ix)) = 100;

* Electrolysis: Correct!
Integer variables N_EL(j,i), N_ES(g,j,i);

Positive variables U_EL_nom(j,i);
Equations eq_U_EL_nom;

eq_U_EL_nom(plt(js,i)) .. U_EL_nom(js,i) =E= N_EL(js,i) * Param('%el%','mn');   // MW



* Energy storage technologies: Correct!
Positive variables U_ES_nom(g,j,i);
Equations eqU_ES_nom;

eqU_ES_nom(es,plt(js,i)) .. U_ES_nom(es,js,i) =E= N_ES(es,js,i) * Param(es,'mn');   // MWh or ton/hr


* RWGS: Correct!
Positive variables U_RWS_nom(j,i), Pi_RWS(j,i);
Equations eqU_RWS_nom;

eqU_RWS_nom(plt(js,i)) .. Pi_RWS(js,i) =E= U_RWS_nom(js,i)/ Param('RWS','mn');   // ton/hr: H2

* MeOH: Correct!
Parameters Pi_MSR(j,i);
Pi_MSR(js,i) = MeOH_Cap_hr(js,i) / Param('MSR','mn'); // ton/hr

Display Pi_MSR;

* ================================ System Operation ================================ *
* Solar and Wind: Correct! 
Positive variables  P_PV(j,ix,h), P_WT(j,ix,h);
Equations eqP_PV, eqP_WT;

eqP_PV(cpv(js,ix),h) .. P_PV(js,ix,h) =E= PV_CF(js,ix,h) * U_RE_nom('PV',js,ix);        // MW
eqP_WT(cwd(js,ix),h) .. P_WT(js,ix,h) =E= OnWind_CF(js,ix,h) * U_RE_nom('WT',js,ix);    // MW

eqP_PV.scale(cpv(js,ix),h) = 0.1;
eqP_WT.scale(cwd(js,ix),h) = 0.1;

* Energy storage technologies: 
Scalars elo   energy loss     / 0.002 /;

Positive variables  En_ES(g,j,i,t), ChgP(g,j,i,h), DisP(es,j,i,h);   // Only cities with methanol plants will deploy storage technologies

* Charging and Discharging modeling: Correct!
Equations eq_ES_balance, eq_Chg_P, eq_Dis_P, eq_Direction;

eq_ES_balance(es,plt(js,i),h(t)) .. En_ES(es,js,i,t) =E= En_ES(es,js,i,t-1) * (1 - elo) + sum(yre, Eta_tech(es,yre)) * ChgP(es,js,i,h) - DisP(es,js,i,h); // MW
eq_Chg_P(es,plt(js,i),h) .. ChgP(es,js,i,h) =L= Param(es,'lm') * U_ES_nom(es,js,i);  // MW
eq_Dis_P(es,plt(js,i),h) .. DisP(es,js,i,h) =L= Param(es,'lm') * U_ES_nom(es,js,i);  // MW
eq_Direction(es,plt(js,i),h) .. ChgP(es,js,i,h) + DisP(es,js,i,h) =L= Param(es,'lm') * U_ES_nom(es,js,i);  // MW

* Energy Capacities: Correct!
Equation eq_Cap;
eq_Cap(es,plt(js,i),h) .. En_ES(es,js,i,h) =L= tau(es) * U_ES_nom(es,js,i);  //MWh

* Initial settings: Correct!
En_ES.fx(es,js,i,'h0')$(plt(js,i)) = 0;
En_ES.fx(es,js,i,h)$(plt(js,i) and (ord(h) = card(h))) = 0;

* ================== Electricity transmision from city ix to i ================*
* City-to-City TNS within province j
Scalars lns   line loss per km  / 0.00001 / ;   // 0.1%/100 km

Positive variables P_city_PV(j,ix,i,h), P_city_WT(j,ix,i,h), P_city(j,ix,i,h)
                   P_exp_PV(j,ix,h), P_exp_WT(j,ix,h), P_exp(j,ix,h), P_imp(j,i,h) ;

*Transmission power balance - From RES to city
Equations eq_P_city_PV, eq_P_city_WT, eq_P_city, eq_P_city_exp;
eq_P_city_PV(cpv(js,ix),h) .. sum(i$imz(js,ix,i), P_city_PV(js,ix,i,h)) + P_exp_PV(js,ix,h) =L= P_PV(js,ix,h);  //MW, Correct!
eq_P_city_WT(cwd(js,ix),h) .. sum(i$imz(js,ix,i), P_city_WT(js,ix,i,h)) + P_exp_WT(js,ix,h) =L= P_WT(js,ix,h);  //MW, Correct!

eq_P_city(imz(js,ix,i),h) .. P_city(js,ix,i,h) =E= P_city_PV(js,ix,i,h) + P_city_WT(js,ix,i,h);                     //MW, Correct!
eq_P_city_exp(res(js,ix),h) .. P_exp(js,ix,h) =E= P_exp_PV(js,ix,h)$(cpv(js,ix)) + P_exp_WT(js,ix,h)$(cwd(js,ix));  //MW, Correct!

*Transmission power balance - city-to-city Constraints (少一个irx-i的约束，限制P_city(js,irx,i,h), 已增加eq_P_city_d)
Parameter U_city_nom(j,ix,i);
U_city_nom(j,ix,i)$(imz(j,ix,i)) = 1.0e4;     // define Parameters instead of Variables to constrain power flows

Equations eq_P_city_a, eq_P_city_b, eq_P_city_c, eq_P_city_d;
eq_P_city_a(umz(js,iim,i),h) .. (P_city(js,iim,i,h) + P_city(js,i,iim,h)) * (1 - lns * cDstn(js,iim,i)) =L= U_city_nom(js,iim,i);   // MW, Correct!
eq_P_city_b(umz(js,iim,i),h) .. P_city(js,iim,i,h) * (1 - lns * cDstn(js,iim,i)) =L= U_city_nom(js,iim,i);   // MW, Correct!
eq_P_city_c(umz(js,iim,i),h) .. P_city(js,i,iim,h)  * (1 - lns * cDstn(js,iim,i)) =L= U_city_nom(js,iim,i);   // MW, Correct!
eq_P_city_d(rmz(js,irx,i),h) ..  P_city(js,irx,i,h) * (1 - lns * cDstn(js,irx,i)) =L= U_city_nom(js,irx,i);   // MW, constrain power flow from irx to i, Correct!

*Summartion of export and import - From RES to province j
Positive variables F_exp(j,h), F_imp(j,h);
Equations eq_F_exp, eq_F_imp;   

eq_F_exp(js,h) .. F_exp(js,h) =E= sum(ix$(res(js,ix)), P_exp(js,ix,h));   // Correct!
eq_F_imp(js,h) .. F_imp(js,h) =E= sum(i$(plt(js,i)), P_imp(js,i,h)) ;     // Correct!

Positive variables F_prov(ln,jx,j,h);
Equations eq_F_prov_exp, eq_F_prov_imp;
* // emz(ln,js,jsx) 是单向集：注意！冗余方程！
eq_F_prov_exp(js,h) .. F_exp(js,h) =E= sum(vmz(ln,js,jsx), F_prov(ln,js,jsx,h));   // 需要认真检查
eq_F_prov_imp(js,h) .. F_imp(js,h) =E= sum(vmz(ln,js,jsx), F_prov(ln,jsx,js,h) * (1 - pln_loss(ln,js,jsx)));   

*Transmission power balance - Prov TNS Constraints
Equations eq_F_prov_a, eq_F_prov_b, eq_F_prov_c;   // 需要认真检查这几个约束方程
eq_F_prov_a(emz(ln,jsx,js),h) .. F_prov(ln,jsx,js,h) * (1 - pln_loss(ln,js,jsx)) =L= U_prov_nom(ln,jsx,js) * %TNS%;   // MW
eq_F_prov_b(emz(ln,jsx,js),h) .. F_prov(ln,js,jsx,h) * (1 - pln_loss(ln,js,jsx)) =L= U_prov_nom(ln,jsx,js) * %TNS%; 
eq_F_prov_c(emz(ln,jsx,js),h) .. (F_prov(ln,js,jsx,h) + F_prov(ln,jsx,js,h)) * (1 - pln_loss(ln,js,jsx)) =L= U_prov_nom(ln,jsx,js) * %TNS%; 
* ================== Energy balance=====================*
Positive variables P_grid(j,i,h), P_EL(j,i,h);
*Energy balance for each  methanol synthesis plant in province j
Equations eq_EB;   // 需要认真检查
eq_EB(plt(js,i),h) ..  P_PV(js,i,h)$(cpv(js,i)) + P_WT(js,i,h)$(cwd(js,i)) 
                       + DisP('LiB',js,i,h) - ChgP('LiB',js,i,h) + P_grid(js,i,h) 
                       + sum(irx$(cpv(js,irx) and rmz(js,irx,i)), P_city_PV(js,irx,i,h) * (1 - lns * cDstn(js,irx,i)))
                       + sum(irx$(cwd(js,irx) and rmz(js,irx,i)), P_city_WT(js,irx,i,h) * (1 - lns * cDstn(js,irx,i)))
                       + sum(iim$(cpv(js,iim) and mmz(js,iim,i)), P_city_PV(js,iim,i,h) * (1 - lns * cDstn(js,iim,i))) 
                       + sum(iim$(cwd(js,iim) and mmz(js,iim,i)), P_city_WT(js,iim,i,h) * (1 - lns * cDstn(js,iim,i)))
                       - (sum(iim$(cpv(js,i) and mmz(js,iim,i)), P_city_PV(js,i,iim,h)) +
                          sum(iim$(cwd(js,i) and mmz(js,iim,i)), P_city_WT(js,i,iim,h)))  
                       + (P_imp(js,i,h) - P_exp(js,i,h))
                       =E= P_EL(js,i,h);

* =================Electrolysis process================== *
Positive Variables   N_EL_on(j,i,h)      Number of electrolysis modules in mode ON for each plant ij at time t;

* Electrolysis technology on-off operation 
Equation eq_EL_Load_min, eq_EL_Load_max, eq_N_EL_on_cons;

eq_EL_Load_min(plt(js,i),h) .. P_EL(js,i,h) =G= Param('%el%','cfn') * Param('%el%','mn') * N_EL_on(js,i,h);
eq_EL_Load_max(plt(js,i),h) .. P_EL(js,i,h) =L= Param('%el%','cfm') * Param('%el%','mn') * N_EL_on(js,i,h);
eq_N_EL_on_cons(plt(js,i),h) .. N_EL_on(js,i,h) =L= N_EL(js,i);

* Ramping           
Equation Eq_EL_ramp_a, Eq_EL_ramp_b;  
Eq_EL_ramp_a(plt(js,i),h)$(ord(h) > 1) .. P_EL(js,i,h) - P_EL(js,i,h-1) =L=  Param('%el%','ro') * N_EL_on(js,i,h) * Param('%el%','mn');
Eq_EL_ramp_b(plt(js,i),h)$(ord(h) > 1) .. P_EL(js,i,h) - P_EL(js,i,h-1) =G= -Param('%el%','ro') * N_EL_on(js,i,h) * Param('%el%','mn');

* =================Mass balance for materials in each processing unit============================ *                                          
Positive variables  M_EL(csp,j,i,h)   Mass flowrate of chemicals involves in technology g at city i province j time t
                    M_RWS(csp,j,i,h)
                    M_MSR(csp,j,i,h)
                    U_RWS_nom_gas(j,i);

* For PEM we have:
Equation eq_EL_H2, eq_EL_H2O, eq_EL_O2;

eq_EL_H2(plt(js,i),h) .. M_EL('H2',js,i,h) =E= (Coeff('%el%','H2','a') * P_EL(js,i,h) + Coeff('%el%','H2','b') * N_EL_on(js,i,h)) * sum(yre, Eta_tech('%el%',yre));
eq_EL_H2O(plt(js,i),h) .. M_EL('H2O',js,i,h) =E= (Coeff('%el%','H2O','a') * P_EL(js,i,h) + Coeff('%el%','H2O','b') * N_EL_on(js,i,h)) * sum(yre, Eta_tech('%el%',yre));
eq_EL_O2(plt(js,i),h) .. M_EL('O2',js,i,h) =E= (Coeff('%el%','O2','a') * P_EL(js,i,h) + Coeff('%el%','O2','b') * N_EL_on(js,i,h)) * sum(yre, Eta_tech('%el%',yre));

eq_EL_H2.scale(plt(js,i),h) = 0.1;
eq_EL_H2O.scale(plt(js,i),h) = 0.1;
eq_EL_O2.scale(plt(js,i),h) = 0.1;   

* For HST we have:
Equation eq_HST_H2;
eq_HST_H2(plt(js,i),h) .. M_RWS('H2',js,i,h) =E= M_EL('H2',js,i,h) - ChgP('HST',js,i,h) + DisP('HST',js,i,h);

* For RWGS we have
Equation eq_RWG_Gas, eq_RWG_CO2, eq_RWG_H2O, eq_RWG_Gas_cap;

eq_RWG_Gas(plt(js,i),h) .. M_RWS('Gas',js,i,h) =E= Coeff('RWS','Gas','a') * M_RWS('H2',js,i,h) + Coeff('RWS','Gas','b') * Pi_RWS(js,i);
eq_RWG_CO2(plt(js,i),h) .. M_RWS('CO2',js,i,h) =E= Coeff('RWS','CO2','a') * M_RWS('H2',js,i,h) + Coeff('RWS','CO2','b') * Pi_RWS(js,i);
eq_RWG_H2O(plt(js,i),h) .. M_RWS('H2O',js,i,h) =E= Coeff('RWS','H2O','a') * M_RWS('H2',js,i,h) + Coeff('RWS','H2O','b') * Pi_RWS(js,i);
eq_RWG_Gas_cap(plt(js,i),h) .. M_RWS('H2',js,i,h) =L= U_RWS_nom(js,i);


eq_RWG_Gas.scale(plt(js,i),h) = 0.1;
eq_RWG_H2O.scale(plt(js,i),h) = 0.1;

* For PEM -> RWGS -> MEOH we have:
Scalar   DoI  degree of integration   / %doi% /;
Equation eq_MSR_link, eq_MSR_Gas;
*Here DOI represents the overall integration degree
eq_MSR_link(plt(js,i),h) ..  M_RWS('Gas',js,i,h) =L= M_MSR('Gas',js,i,h);

*城市集成度为50%
*eq_MSR_Gas(plt(js,i),h) ..  M_RWS('Gas',js,i,h) =E= DoI * M_MSR('Gas',js,i,h);

*省内集成度为50%
*eq_MSR_Gas(js) .. sum((i,h), nds * M_RWS('Gas',js,i,h)$plt(js,i)) =E= DoI * sum((i,h), nds * M_MSR('Gas',js,i,h)$plt(js,i));


*全国集成度为50%
eq_MSR_Gas .. sum((plt(js,i),h), M_RWS('Gas',js,i,h)) =L=  sum((plt(js,i),h), M_MSR('Gas',js,i,h));

*For MEOH we have:
positive variable M_MSR_htotal_kton(j,i);
Equation eq_MSR_MeOH, eq_MSR_hour_total, eq_MSR_annual;

eq_MSR_MeOH(plt(js,i),h) .. M_MSR('MeOH',js,i,h) =E= Coeff('MSR','MeOH','a') * M_MSR('Gas',js,i,h) + Coeff('MSR','MeOH','b') * Pi_MSR(js,i);
eq_MSR_hour_total(plt(js,i)) .. M_MSR_htotal_kton(js,i) * ths =E= sum(h, nds * M_MSR('MeOH',js,i,h));
eq_MSR_annual(plt(js,i)) .. M_MSR_htotal_kton(js,i) =E= MeOH_Cap_yr(js,i) ;

eq_MSR_hour_total.scale(plt(js,i)) = 10;

* Chemical reaction operational flexibility
Positive variable U_MSR_nom_gas(j,i);
Equation  eq_RWG_min, eq_RWG_max, eq_MSR_min, eq_MSR_max;

eq_RWG_min(plt(js,i),h) .. M_RWS('gas',js,i,h) =G= Param('RWS','cfn') * U_RWS_nom_gas(js,i);
eq_RWG_max(plt(js,i),h) .. M_RWS('gas',js,i,h) =L= Param('RWS','cfm') * U_RWS_nom_gas(js,i);
eq_MSR_min(plt(js,i),h) .. M_MSR('MeOH',js,i,h) =G= Param('MSR','cfn') * MeOH_Cap_hr(js,i);
eq_MSR_max(plt(js,i),h) .. M_MSR('MeOH',js,i,h) =L= Param('MSR','cfm') * MeOH_Cap_hr(js,i);

* Ramping           
Equation Eq_RWS_ramp_a, Eq_RWS_ramp_b;  
Eq_RWS_ramp_a(plt(js,i),h)$(ord(h) > 1) .. M_RWS('gas',js,i,h) - M_RWS('gas',js,i,h-1) =L=  Param('RWS','ro') * U_RWS_nom_gas(js,i);
Eq_RWS_ramp_b(plt(js,i),h)$(ord(h) > 1) .. M_RWS('gas',js,i,h) - M_RWS('gas',js,i,h-1) =G= -Param('RWS','ro') * U_RWS_nom_gas(js,i);

Equation Eq_MSR_ramp_a, Eq_MSR_ramp_b;  
Eq_MSR_ramp_a(plt(js,i),h)$(ord(h) > 1) .. M_MSR('MeOH',js,i,h) - M_MSR('MeOH',js,i,h-1) =L=  Param('MSR','ro') * MeOH_Cap_hr(js,i);
Eq_MSR_ramp_b(plt(js,i),h)$(ord(h) > 1) .. M_MSR('MeOH',js,i,h) - M_MSR('MeOH',js,i,h-1) =G= -Param('MSR','ro') * MeOH_Cap_hr(js,i);

* CO2 Emission and Recycle calculation
Parameters CO2CtM   Carbon emission for each tone of methanol produced [tco2 per tonne] /4.368/
           xi_capt  coefficient of carbon capture rate / 0.6 /;

Positive variables MeOH_coal_hr(js,i,h), CO2_coal(js,i,h), CO2_capt(js,i,h), CO2_pur(js,i,h), CO2_em(js,i,h);
Equation Eq_MeOH_coal_hr, Eq_CO2_coal, Eq_capt_const1, Eq_capt_const2, Eq_CO2_balance1, Eq_CO2_balance2;

Eq_MeOH_coal_hr(plt(js,i),h) .. MeOH_coal_hr(js,i,h) =E= M_MSR('MEOH',js,i,h) - (M_RWS('Gas',js,i,h) * Coeff('MSR','MeOH','a') + Coeff('MSR','MeOH','b') * Pi_MSR(js,i));
Eq_CO2_coal(plt(js,i),h) .. CO2_coal(js,i,h) =E= MeOH_coal_hr(js,i,h) * CO2CtM;
Eq_capt_const1(plt(js,i),h) .. CO2_capt(js,i,h) =L= M_RWS('CO2',js,i,h);
Eq_capt_const2(plt(js,i),h) .. CO2_capt(js,i,h) =L= CO2_coal(js,i,h) * xi_capt;
Eq_CO2_balance1(plt(js,i),h) .. CO2_coal(js,i,h) =E= CO2_em(js,i,h) + CO2_capt(js,i,h);
Eq_CO2_balance2(plt(js,i),h) .. M_RWS('CO2',js,i,h) =E= CO2_pur(js,i,h) + CO2_capt(js,i,h);

* =======================================================Price evaluation============================================= *
* ================================ Section Breakup ====================================*

Scalars ir         interst rate                       / 0.05 /
        uH2O       water cost [$ per tonne]           / 0.362 /
        uO2        O2 COST [$ per tonne]              / 63.57 /
        City_VOM   Electricity TNS cost between cities within province [USD per MWh] / 0.169 /;
        
Parameters  CRF(g)
            Prov_VOM(ln)   Electricity TNS cost between provinces [USD per MWh] / AC 5.37, DC 5.37 /;
//Prov_VOM：            

CRF(g) = (ir * (1 + ir) ** sum(yre, Param_ltm(g,yre))) / ((1 + ir) ** sum(yre, Param_ltm(g,yre)) - 1);
Display CRF;


* ================PV AND WT================== *
Positive Variables Capex_RE(rg,j,ix), FOM_RE(rg,j,ix);
Equation eq_Capex_RE, eq_FOM_RE;

eq_Capex_RE(rg,res(js,ix)) .. Capex_RE(rg,js,ix) =E=  CRF(rg) * sum(yre, Tech_CAP(rg,yre) * U_RE_nom(rg,js,ix));
eq_FOM_RE(rg,res(js,ix)) .. FOM_RE(rg,js,ix) =E= sum(yre, Tech_FOM(rg,yre) * U_RE_nom(rg,js,ix));

* ===============Electrolysis technology============== *
Positive Variables Capex_EL(j,i), FOM_EL(j,i), VOM_EL(j,i);
Equation eq_Capex_EL, eq_FOM_EL, eq_VOM_EL;

eq_Capex_EL(plt(js,i)) .. Capex_EL(js,i) =E= CRF('%el%') * sum(yre, Tech_CAP('%el%',yre) * U_EL_nom(js,i));
eq_FOM_EL(plt(js,i)) .. FOM_EL(js,i) =E= sum(yre,  Tech_FOM('%el%',yre) * U_EL_nom(js,i));
eq_VOM_EL(plt(js,i)) .. VOM_EL(js,i) =E= sum((yre,h), Tech_VOM('%el%',yre) * nds * P_EL(js,i,h));

eq_VOM_EL.scale(plt(js,i)) = 0.01;

* ===============RWGS reactor============== *
Positive Variables Capex_RWS(j,i), FOM_RWS(j,i), VOM_RWS(j,i);
Equation eq_Capex_RWS, eq_FOM_RWS, eq_VOM_RWS;

eq_Capex_RWS(plt(js,i)) .. Capex_RWS(js,i) =E= CRF('RWS') * sum(yre, Tech_CAP('RWS',yre) * U_RWS_nom_gas(js,i));
eq_FOM_RWS(plt(js,i)) .. FOM_RWS(js,i) =E= sum(yre, Tech_FOM('RWS',yre) * U_RWS_nom_gas(js,i));
eq_VOM_RWS(plt(js,i)) .. VOM_RWS(js,i) =E= sum((yre,h), Tech_VOM('RWS',yre) * nds * M_RWS('Gas',js,i,h));
eq_VOM_RWS.scale(plt(js,i)) = 0.01;

* ===============Storage technology======================= *
Positive Variables Capex_ES(es,j,i), FOM_ES(es,j,i), VOM_ES(es,j,i);
Equation eq_Capex_ES, eq_FOM_ES, eq_VOM_ES;

eq_Capex_ES(es,plt(js,i)) .. Capex_ES(es,js,i) =E= CRF(es) * sum(yre, Tech_CAP(es,yre) * U_ES_nom(es,js,i));
eq_FOM_ES(es,PLT(js,i)) .. FOM_ES(es,js,i) =E= sum(yre, Tech_FOM(es,yre) * U_ES_nom(es,js,i));
eq_VOM_ES(es,PLT(js,i)) .. VOM_ES(es,js,i) =E= sum((yre,h), Tech_VOM(es,yre) * nds * (ChgP(es,js,i,h) + DisP(es,js,i,h))) ;

eq_VOM_ES.scale(es,PLT(js,i)) = 0.01

* ===============City-to-city Transmission line============*
Positive Variables VOM_Pcity(j,ix,i), VOM_Pprov(ln,js,j);
Equation eq_VOM_Prcity, eq_VOM_Pmcity, eq_VOM_Pprov;
eq_VOM_Prcity(rmz(js,irx,i)) .. VOM_Pcity(js,irx,i) * ths =E= sum(h, nds * City_VOM * (P_city(js,irx,i,h)));
eq_VOM_Pmcity(mmz(js,iim,i)) .. VOM_Pcity(js,iim,i) * ths =E= sum(h, nds * City_VOM * (P_city(js,iim,i,h)));
eq_VOM_Pprov(vmz(ln,jsx,js)) .. VOM_Pprov(ln,jsx,js) * ths =E= sum(h, nds * Prov_VOM(ln) * (F_prov(ln,jsx,js,h)));  // 注意双向流动

* ===============Electricity purchasing==================== *
Positive variables E_Purs(j,i);
Equation eq_E_Purs;

eq_E_Purs(plt(js,i)) .. E_Purs(js,i) =E= sum(h, nds * tou(js,h) * %TOU% **(%yl%) * P_grid(js,i,h)); //$/kWh -> k$/MWh

eq_E_Purs.scale(plt(js,i)) = 0.1;

* ===============Water and CO2 purchasing, O2 selling ======================== *
Positive variables  FSC_H2O(j,i), FSC_O2(j,i), FSC_CO2(js,i), FSC_CO2e(js,i), FSC_CO2p(js,i), FSC_CO2c(js,i);
Equation eq_FSC_H2O, eq_FSC_O2, eq_FSC_CO2e, eq_FSC_CO2p, eq_FSC_CO2c;

eq_FSC_H2O(plt(js,i)) .. FSC_H2O(js,i) * ths =E= uH2O * sum(h, nds * (M_EL('H2O',js,i,h) - M_RWS('H2O',js,i,h)));
eq_FSC_O2(plt(js,i)) .. FSC_O2(js,i) * ths =E= uO2 * sum(h, nds * M_EL('O2',js,i,h)) ;

eq_FSC_CO2e(plt(js,i)).. FSC_CO2e(js,i) * ths =E= (sum(yre, uCO2e(yre)) * sum(h, nds * CO2_em(js,i,h)));
eq_FSC_CO2p(plt(js,i)).. FSC_CO2p(js,i) * ths =E= (sum(yre, uCO2p(yre)) * sum(h, nds * CO2_pur(js,i,h)));
eq_FSC_CO2c(plt(js,i)).. FSC_CO2c(js,i) * ths =E= (sum(yre, uCO2c(yre)) * sum(h, nds * CO2_capt(js,i,h)));

* =================================================Summation===========================================*
Variables Capex(j), FOM(j), VOM(j), EPC(j), TFSC_H2O(j), TFSC_O2(j), TFSC_CO2e(j), TFSC_CO2p(j), TFSC_CO2c(j), TFSC_CO2(j), TAC_prov(j), TAC;


Equation eq_Capex, eq_FOM, eq_VOM, eq_EPC, eq_H2O, eq_O2, eq_CO2, eq_CO2e, eq_CO2p, eq_CO2c, eq_TAC_prov, eq_TAC; 

eq_CAPEX(js) .. Capex(js) =E= sum((rg,ix), Capex_RE(rg,js,ix)$res(js,ix)) + 
                              sum(i$plt(js,i), Capex_EL(js,i)) + 
                              sum(i$plt(js,i), Capex_RWS(js,i)) +
                              sum((es,i), Capex_ES(es,js,i)$plt(js,i)) ;

eq_FOM(js) .. FOM(js) =E= sum((rg,ix), Fom_RE(rg,js,ix)$res(js,ix)) + 
                          sum(i$plt(js,i), FOM_EL(js,i)) +
                          sum(i$plt(js,i), FOM_RWS(js,i)) +
                          sum((es,i), FOM_ES(es,js,i)$plt(js,i)) ;
                          
eq_VOM(js) .. VOM(js) =E= sum(i$plt(js,i), VOM_EL(js,i)) + 
                          sum((es,i), VOM_ES(es,js,i)$plt(js,i))+
                          sum(i$plt(js,i), VOM_RWS(js,i))+
                          sum((ix,i)$(imz(js,ix,i)), VOM_Pcity(js,ix,i)) +
                          sum((ln,jsx)$(vmz(ln,jsx,js)), VOM_Pprov(ln,jsx,js));
                          
eq_EPC(js) .. EPC(js) =E= sum((i,plt(js,i)), E_Purs(js,i));

eq_H2O(js) .. TFSC_H2O(js) =E= sum((i,plt(js,i)), FSC_H2O(js,i));

eq_O2(js) .. TFSC_O2(js) =E= sum((i,plt(js,i)), FSC_O2(js,i));

eq_CO2e(js) .. TFSC_CO2e(js) =E= sum((i,plt(js,i)), FSC_CO2e(js,i));

eq_CO2p(js) .. TFSC_CO2p(js) =E= sum((i,plt(js,i)), FSC_CO2p(js,i));

eq_CO2c(js) .. TFSC_CO2c(js) =E= sum((i,plt(js,i)), FSC_CO2c(js,i));

eq_CO2(js) ..  TFSC_CO2(js) =E= TFSC_CO2e(js) + TFSC_CO2p(js) + TFSC_CO2c(js);

eq_TAC_prov(js) .. TAC_prov(js) =E= Capex(js) + FOM(js) + VOM(js) + EPC(js) + TFSC_H2O(js) + TFSC_CO2(js) - TFSC_O2(js);    


eq_TAC .. TAC =E=  sum(js, TAC_prov(js));

* ===================================Coal-based OM cost evaluation================================= *
*ref:A multi-dimensional feasibility analysis of coal to methanol assisted by green hydrogen from a life cycle viewpoint
* Coal to mehtanol conversion rate: Study on coal to methanol of Arutmin coal
Scalars Coal_FOM        Reference FOM of coal-syngas generating / 377 /
        Coal_VOM        Reference VOM of coal-syngas generating / 0.0257 /
        CtM             Reference coal-to-methanol ratio / 1.25837 / //1.25837
        CtMW            Reference coal-to-methanol water requirement / 4.23 / //1.53715 - 用LCWC替代
        ECtM            Electricity consumption for each tone of in the coal-based routine [MWh per tonne] / 1.731951 /;
        
Positive variables MeoH_coal_nom(j,i), FOM_coal_city(j,i), VOM_coal_city(j,i), FSC_coal_city(j,i), FSC_cwater_city(j,i), FSC_eC_city(j,i);

Equation Eq_MeoH_coal_nom, FOM_coal_i, Vom_coal_i, FSC_coal_i, FSC_water_i, FSC_eC_i;

Eq_MeoH_coal_nom(plt(js,i),h) ..  MeOH_coal_hr(js,i,h) =L= MeoH_coal_nom(js,i);

FOM_coal_i(plt(js,i)) .. FOM_coal_city(js,i) =E= MeoH_coal_nom(js,i) * Coal_FOM ;
FOM_coal_i.scale(plt(js,i)) = 10;

Vom_coal_i(plt(js,i)) .. VOM_coal_city(js,i) =E= sum(h, nds * MeOH_coal_hr(js,i,h)) * Coal_VOM ;

FSC_coal_i(plt(js,i)) .. FSC_coal_city(js,i) =E= sum(h, nds * MeOH_coal_hr(js,i,h))/ths * CtM * sum(yre, uCoal(yre)); 

FSC_water_i(plt(js,i)) .. FSC_cwater_city(js,i) =E= sum(h, nds * MeOH_coal_hr(js,i,h))/ths * CtMW * uH2O;  // ktonne in year compensate with k$

FSC_eC_i(plt(js,i)) .. FSC_eC_city(js,i) =E= sum(h, MeOH_coal_hr(js,i,h) * ECtM * tou(js,h) * %TOU% **(%yl%) ); //k$
FSC_eC_i.scale(plt(js,i)) = 0.1;
* ================================Sum up for coal================================ *
Positive variables FOM_coal(j), FSC_coal_prov(j), FSC_cwater_prov(j), FSC_eC_prov(js), VOM_coal(j) , TAC_coal_prov_wi(j), TAC_coal_wi;

Equation Eq_FOM_coal, Eq_FSC_coal_prov, Eq_FSC_cwater_prov, Eq_FSC_eC_prov, Eq_VOM_coal, Eq_TAC_coal_prov_wi, Eq_TAC_coal_wi;
Eq_FOM_coal(js) .. FOM_coal(js) =E= sum(i$(plt(js,i)), FOM_coal_city(js,i));

Eq_FSC_coal_prov(js) .. FSC_coal_prov(js) =E= sum(i$(plt(js,i)), FSC_coal_city(js,i));

Eq_FSC_cwater_prov(js) .. FSC_cwater_prov(js) =E= sum(i$(plt(js,i)), FSC_cwater_city(js,i));

Eq_FSC_eC_prov(js) .. FSC_eC_prov(js) =E= sum(i$(plt(js,i)), FSC_eC_city(js,i)); //k$

Eq_VOM_coal(js) .. VOM_coal(js) =E= FSC_cwater_prov(js) + FSC_eC_prov(js) + sum(i$(plt(js,i)), VOM_coal_city(js,i));

Eq_TAC_coal_prov_wi(js) .. TAC_coal_prov_wi(js) =E= FOM_coal(js) + VOM_coal(js) + FSC_coal_prov(js);

Eq_TAC_coal_wi .. TAC_coal_wi =E= sum(js, TAC_coal_prov_wi(js));


* ===================================Methanol synthesis OM cost evaluation================================= *
Scalars Msyn_FOM   Reference FOM of methanol synthesis and distillating / 23.6 /    //$k/(ton/hr)/yr
        Msyn_VOM   Reference VOM of coal-syngas generating    / 0.003 /  //$k/ton 
        EStM       Electricity consumption for each tone of in the synthesis [MWh per tonne] / 1.254 /;
        
Parameters FOM_Msyn_prov(j), VOM_Msyn_prov(j), TAC_Msyn_prov(j), FSC_eM_city(j), TAC_Msyn;

FOM_Msyn_prov(js) = sum(i$(plt(js,i)), MeOH_Cap_hr(js,i) * Msyn_FOM);

FSC_eM_city(js) = sum((plt(js,i),h), MeOH_Cap_hr(js,i) * ECtM * tou(js,h) * %TOU% **(%yl%)); //k$

VOM_Msyn_prov(js) = FSC_eM_city(js) + sum(i$(plt(js,i)), MeOH_Cap_yr(js,i) * ths * Msyn_VOM);

TAC_Msyn_prov(js) = FOM_Msyn_prov(js) + VOM_Msyn_prov(js);

TAC_Msyn = sum(js, TAC_Msyn_prov(js));


* ===============Economic output define======================= *
$ontext
Parameter MeOH_Cap_prov(j);

MeOH_Cap_prov(js) = sum(i$plt(js,i), MeOH_Cap_yr(js,i));


VARIABLE CTAC, MTAC, Coal_degree, Coal_degree_scale, LCOM;

Parameter MeOH_cap_yr_Mton(j,i);
MeOH_cap_yr_Mton(js,i) = MeOH_Cap_yr(js,i)/ths;

Equation Eq_Coal_degree1, Eq_Coal_degree2, Eq_CTAC_BLN, Eq_CTAC, Eq_MTAC, Eq_LCOM;

Eq_Coal_degree1 .. Coal_degree_scale =E= sum((js,i,h), nds * MeOH_coal_hr(js,i,h)$plt(js,i)) / sum(plt(js,i), MeOH_cap_yr_Mton(js,i));
Eq_Coal_degree2 .. Coal_degree =E= Coal_degree_scale / ths / ths;
Coal_degree.up= 1;
Eq_Coal_degree2.scale = 0.001;

Parameter TAC_coal_wi_BLN;
TAC_coal_wi_BLN = TAC_coal_wi/ths/ths ;
Display TAC_coal_wi, TAC_coal_wi_BLN;

Positive Variable CTAC_BLN;

Eq_CTAC_BLN .. CTAC_BLN =E= TAC_coal_wi_BLN * Coal_degree;
Eq_CTAC .. CTAC =E= CTAC_BLN * ths * ths;
Eq_CTAC.scale = 1000;
$offText
Variable  MTAC, LCOM;
Equation Eq_MTAC, Eq_LCOM;

Eq_MTAC .. MTAC =E= TAC + TAC_coal_wi + TAC_Msyn;
Eq_MTAC.scale = 100;


Eq_LCOM .. LCOM =E= MTAC / sum(plt(js,i), MeOH_Cap_yr(js,i));
Eq_LCOM.scale = 1e-3;

$ontext 
$Set flag 1

Variables OBJ;
Equations eqOBJ;

$ifthen "%flag%" == "1"
eqOBJ .. OBJ =E= TAC;

$elseif "%flag%" == "2"
eqOBJ .. OBJ =E= DTAC;

$elseif "%flag%" == "3"
eqOBJ .. OBJ =E= LCOM;

$endif
$offText

$onText
Variables TAC;
Equations eq_TAC;
eq_TAC .. TAC =E= 0;
$offText

Model MeOH / all /;

Options mip = gurobi, optcr = 0.01, reslim = 2592000, limrow = 0, limcol = 0, solprint = on, sysout = off;

MeOH.scaleopt = 1;
MeOH.Cutoff = 1E8;
$onEcho > gurobi.opt
method 2
threads 48
ScaleFlag 1
BarHomogeneous 1
FeasibilityTol 1e-5
OptimalityTol 1e-5
BarConvTol 1e-6
iis 1
$offEcho

MeOH.optfile = 1;

Solve MeOH using mip minimizing MTAC;

Parameters
CO2ETM;

CO2ETM = sum((js,i,h), M_RWS.l('CO2',js,i,h)) / (DOI * sum((js,i,h),M_MSR.l('MEOH',js,i,h)));

display CO2ETM;

* ============DOI evaluation ===================*
Parameter   DoI_city(j,i)  Degree of integration for each city
            DoI_prov(j)    degree of integration for each province;
            
            
DoI_city(plt(js,i))  = sum(h, M_RWS.l('Gas',js,i,h)) / sum(h, M_MSR.l('Gas',js,i,h));
DoI_prov(js)  = (sum((i,h), M_RWS.l('Gas',js,i,h)$plt(js,i))) / (sum((i,h), M_MSR.l('Gas',js,i,h)$plt(js,i)));

Display DoI_city, DoI_prov;

* ==========================Evaluation of TAC_PROV============================ *
Parameters DLCOR, LCOC, DLCOR_prov(j), LCOM_prov(j), DLCOR;

LCOM_prov(js) = (TAC_prov.l(js) + TAC_coal_prov_wi.l(js) * (1 - DoI_prov(js)) + TAC_Msyn_prov(js)) / sum(i$plt(js,i), MeOH_Cap_yr(js,i));

Display LCOM_prov;


* ====================Data gathering============================= *
Parameters U_nom(j,ix,g), N_modules(j,i,g);

U_nom(js,ix,rg) = U_RE_nom.l(rg,js,ix);
U_nom(js,i,'%el%') = U_EL_nom.l(js,i);
U_nom(js,i,es) = U_ES_nom.l(es,js,i);
U_nom(js,i,'RWS') = U_RWS_nom.l(js,i);
U_nom(js,i,'MSR') = MeOH_Cap_yr(js,i);

N_modules(js,i,'%el%') = N_EL.L(js,i);
N_modules(js,i,es) = N_ES.L(es,js,i);

Parameters DOI_optimized;

DOI_optimized = (sum((plt(js,i),h), M_RWS.l('Gas',js,i,h)))/(sum((plt(js,i),h), M_MSR.l('Gas',js,i,h)));

Display DOI_optimized;

* ================Carbon Emission define======================= *
Scalar PV_CO2  Carbon emission factor throughout full life cyc of PV [tonne per MWh] / 0.0142 /
       WT_CO2  Carbon emission factor throughout full life cyc of PV [tonne per MWh] / 0.01 /; 
Parameters RLCCE_prov(js) Carbon emission for retrofit system
           RLCCE;

*RLCCE_city(plt(js,i)) = (sum(h, nds * PV_CO2 * P_PV.l(js,i,h)) + sum(h, nds * WT_CO2 * P_WT.l(js,i,h)) + sum(h, CF_CO2(js) * nds * P_grid.l(js,i,h))- sum(h, nds * M_RWS.l('CO2',js,i,h)))/(MeOH_Cap_yr(js,i)*ths) - CO2CtM;

RLCCE_prov(js)$(DOI_prov(js)>0) = (sum((i,h), nds * PV_CO2 * P_PV.l(js,i,h)) + sum((i,h), nds * WT_CO2 * P_WT.l(js,i,h)) + sum((i,h,yre), CF_CO2(js,yre) * nds * P_grid.l(js,i,h))- sum((i,h), nds * M_RWS.l('CO2',js,i,h)) + sum((i,h),nds * CO2_em.l(js,i,h)))/sum(i, MeOH_Cap_yr(js,i) * ths);
RLCCE = (sum((js,i,h), nds * PV_CO2 * P_PV.l(js,i,h)$plt(js,i)) + sum((js,i,h), nds * WT_CO2 * P_WT.l(js,i,h)$plt(js,i)) + sum((js,i,h,yre), CF_CO2(js,yre) * nds * P_grid.l(js,i,h)$plt(js,i))- sum((js,i,h), nds * M_RWS.l('CO2',js,i,h)$plt(js,i)) + sum((js,i,h),nds * CO2_em.l(js,i,h)$plt(js,i)))/sum((js,i), MeOH_Cap_yr(js,i) * ths);

Display RLCCE_prov, RLCCE;


Execute_Unload '%Sfolder%S_PEM_2040_Opt.gdx' yre, DOI, U_nom, N_modules, P_PV, P_WT, En_ES, ChgP, DisP, P_city_PV, P_city_WT, P_city, P_exp_PV, P_exp_WT, P_exp, P_imp
                                     U_city_nom, F_exp, F_imp, F_prov, P_grid, P_EL, N_EL_on, M_EL, M_RWS, M_MSR, MeOH_coal_hr
                                     CO2_coal, CO2_capt, CO2_pur, CO2_em, Capex_RE, FOM_RE, Capex_EL, FOM_EL, VOM_EL, Capex_ES, FOM_ES, VOM_ES, Capex_RWS, FOM_RWS, VOM_RWS
                                     VOM_Pcity, VOM_Pprov, E_Purs, FSC_H2O, FSC_O2, FSC_CO2, FSC_CO2e, FSC_CO2p, FSC_CO2c, Capex, FOM, VOM, EPC,
                                     TFSC_H2O, TFSC_O2, TFSC_CO2e, TFSC_CO2p, TFSC_CO2c, TFSC_CO2, TAC_prov, TAC
                                     DoI_city, DoI_prov, FOM_coal_city, FSC_coal_city, FSC_cwater_city, FSC_eC_city, 
                                     FOM_coal, VOM_coal, FSC_coal_prov, FSC_cwater_prov, FSC_eC_prov, TAC_coal_prov_wi, TAC_coal_prov_wi
                                     FOM_Msyn_prov, VOM_Msyn_prov, TAC_Msyn_prov, TAC_Msyn,
                                     DLCOR, MTAC, LCOM, LCOC, DLCOR_prov, LCOM_prov, RLCCE, RLCCE_prov, DOI_optimized;