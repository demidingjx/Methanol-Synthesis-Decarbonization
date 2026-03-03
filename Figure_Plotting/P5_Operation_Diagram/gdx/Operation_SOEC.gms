$eolCom //
$Set EL  SOE    
$Set TN  SST
$Set rs  288
$Set YR  2040
$Set ED  ED50
$Set Disk E
$Set folder GDX7_M12_Fix
$Set Sens HEL


*输入gdx文件 - Define the gdx file path (GDX1_M12,记得改年份)
$Set Sfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\%folder%\%EL%\%YR%\%ED%\

*输出excel文件 - Define the output excel location (LCOM，年份)
$Set Cfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\P5_Operation_Diagram\Excel\

*相关Data
$Set Dfolder %Disk%:\2025_Methanol_synthesis\3_GAMS\csv_Single_Prov\


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

*---------------------读数据----------------------------*
Parameter U_nom(j,ix,pg), P_PV(j,ix,h), P_WT(j,ix,h), P_EL(j,i,h), ChgP(es,j,i,h), DisP(es,j,i,h)
          P_grid(j,i,h), MeOH_coal_hr(j,i,h), M_MSR(csp,j,i,h), En_ES(es,j,i,h);

$gdxin %Sfolder%S_%EL%_%YR%_%ED%.gdx
$load U_nom = U_nom.l, P_PV = P_PV.l, P_WT = P_WT.l, P_EL = P_EL.l, ChgP = ChgP.l, DisP = DisP.l, P_grid = P_grid.l, MeOH_coal_hr = MeOH_coal_hr.l, M_MSR = M_MSR.l, En_ES = En_ES.l
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

Execute_Unload 'Dynamic_%EL%_%YR%_%ED%.gdx' Tol_P_PV, Tol_P_WT, Tol_P_EL, Tol_ChgP_LiB, Tol_DisP_LiB, Tol_ChgP_tank, Tol_DisP_tank, Tol_En_ES_LiB, Tol_En_ES_tank, Tol_P_grid, Tol_MeOH_coal_hr, Tol_M_MSR;
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
$offEcho

//记得对应技术、年份与ED
execute 'gdxxrw Dynamic_%EL%_%YR%_%ED%.gdx output = %Cfolder%Hourly_%EL%_%YR%_%ED%.xlsx @Dynamicoperation_%el%.txt';










