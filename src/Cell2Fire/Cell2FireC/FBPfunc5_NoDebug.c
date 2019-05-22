/*   Subroutine of  FBP.C   version 4.4   Aug,2007
         Canadian Forest Fire Behaviour Prediction System
This code is copyright of the Canadian Forest Service, Natural Resources Canada (1992-2005)
It is provide free of charge to anyone who wishes to incorporate it within their 
forest fire management applications, however users should note in their application that
the FBP calucaltions come from the Canadianf Forest Services Fire Behaviour Prediction
System. The Canadian Forest Service has gone through considerable testing to ensure that
these computer functions duplicate the system as laid out in ST-X-3 (The Development
and Structure of the Canadian Forest Fire Behaviour Prediction System (1992)) and the subsequent corrections and additions to the system (the draft "FBP Note"), however no
guarentte is given as to the absolute accuracy of the code.
  This file contains a series of functions that go thru all the
  FBP System calculations.
Originally  Written at P.N.F.I.  December 91, by Mike Wotton
 Corrections to version  1.0
   1.01  -  b value in O1b was wrong.   KA at nofc (mar5,92) ...bmw
   1.01a  - no error just added upper and lowercase fueltype entry ...bmw
   1.02   - l_to_b problem with inequalitiy...minor prob fixed
   1.5  - modifications to stop small(improbable) numbers from blowing
          up the slope calculation stuff
          this caused a slope problem which BA @ PFC pointed out
                may 93.......bmw
   3.0  jan /96   bmw
        -  c6  - constant sfc
      3.01  apr/97
        - add line to recognize uppercase in grass fuels
      3.02  apr/97
        - change accn funtion to recognize lower case fuels for open
      3.1  jul/97
        - change slope function to stop overflow when cur<=50 in O1
      3.2 sept/97
        - change the c6 calc of flank ros to avoid variation in l/b with
           RSC calculation in flank.
      3.3 jan/98
        - error was SFC >0  if CUR<50 (and hence ROS=0)
          changed this within the surf_fuel_consump() fn
      3.4 apr/98  (ya i know the dates aren't in sequence)
         - change O1a  A value from 1.41 to 1.4  from KA apr/98
         
      4.0 jan/98
         - changes listed within the FBP note and TEST dataset 
        4.1  - August 2004
          - final changes in the FBP note (new M-3/M-4 model) and a new grass CF model
        -removed some verstigaes of older functions for input /output
        4.2 - Oct 2004
        - changes as a result of discussion with Prometheus team
         -  SFC in grass ...4.1 did not include changes to grass consumption though
            spread at values of CUR<50% are now possible (see point 3.3 above)
        - at  very short time periods using acceleration a CFB(t) should be caluclated
            and used for final ROS in the C-6 model. 
       4.3 - August 2005
        - changes as a result of further discussions with Prometheus team. These were:
        - changes to include the alternate ISI calculation formula (53a footnote 2) in 
                the calculation of WSE  (...added as a section to The FBP Note)
        - addition of D-2 for the promtheus team to evaluate their model
          ( D-2 is leafed out pure aspen
            ROS(D-2)= 0.2 * ROS(D-1) if BUI>80  otherwise ROS(D-2)=0)
        - NOTE that this (D-2) is not an official part of the FBP System however.
        4.4  August 2007
         - crown consump in m3/m4. It was calcuating based full conifer content.
                but should be modifed by PDF
         - change to match changes in FBP Note section 3.3 (eqn 66c)
        4.5 Nov 2007
          - perimeter calc wasn't based on LB(t).
          - Flankfire final ROS (FROS) could be set to FRSS if flank fire did not
             involve crowning 
          - change to function headers in perimeter() and  flank_spread_distance()
                to accomodate LB(t) assignment
          - LB(t) is now added to the secondary inputs structure and kept
                it is asdsigned in  flank_spread_distance().
        4.6 jan 2009
          - uping the slope limit to 70%...and so the default after that is 10.0
        5.0  Oct 2014
            - PGR is corrected to be a function of ROS(t) not equilibrium ROS  
        5.0001  June 2015
            - forgot to change the encoded version number to 5.0.  now 5.0001
            - updated header to FBP5.h
*/

#include "FBP5.0.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

  char version[50]="Last modified June 2015,  by BMW ",
       ver[17] = "Version 5.0001  ";

  float slopelimit_isi=0.01, numfuels=18;

  void calculate(inputs *data,fuel_coefs *pt,main_outs *at,
      snd_outs *sec,fire_struc *hptr,fire_struc *fptr,fire_struc *bptr)
  {
    char firetype;
    float accn;
    fuel_coefs **ptr=&pt;
    zero_main(at);
    zero_sec(sec);
    zero_fire(hptr);
    zero_fire(fptr);
    zero_fire(bptr);
    at->covertype=get_fueltype_number(ptr,data->fueltype);
    at->ff=ffmc_effect(data->ffmc);
    at->rss=rate_of_spread(data,(*ptr),at);
    hptr->rss=at->rss;
    at->sfc=surf_fuel_consump(data);
    at->sfi=fire_intensity(at->sfc,at->rss);


    if(at->covertype=='c')
     {
       at->fmc=foliar_moisture(data,at);
       at->csi=crit_surf_intensity((*ptr),at->fmc);
       at->rso=critical_ros(data->fueltype,at->sfc,at->csi);
       firetype=fire_type(at->csi,at->sfi);


       if(firetype=='c')
        {
         hptr->cfb=crown_frac_burn(at->rss,at->rso);
         hptr->fd=fire_description(hptr->cfb);
         hptr->ros=final_ros(data,at->fmc,at->isi,hptr->cfb,at->rss);
         hptr->cfc=crown_consump(data,(*ptr),hptr->cfb);
         hptr->fc=hptr->cfc+at->sfc;
         hptr->fi=fire_intensity(hptr->fc,hptr->ros);
        }
     }
    if(at->covertype=='n' || firetype=='s')
     {
      hptr->fd='S';
      hptr->ros=at->rss;
      hptr->fc=at->sfc;
      hptr->fi=at->sfi;
      hptr->cfb=0.0;
     }
    sec->lb=l_to_b(data->fueltype,at->wsv);
    bptr->isi=backfire_isi(at);
    bptr->rss=backfire_ros(data,(*ptr),at,bptr->isi);
    fptr->rss=flankfire_ros(hptr->rss,bptr->rss,sec->lb);
    bptr->fi=fire_behaviour(data,(*ptr),at,bptr);
    fptr->ros=flankfire_ros(hptr->ros,bptr->ros,sec->lb );
    fptr->fi=flank_fire_behaviour(data,(*ptr),at,fptr);

    if(data->pattern==1 && data->time>0)
      {
        accn=acceleration(data,hptr->cfb);
        hptr->dist=spread_distance(data,hptr,accn);
        bptr->dist=spread_distance(data,bptr,accn);
        fptr->dist=flank_spread_distance(data,fptr,sec,hptr->rost,bptr->rost,
            hptr->dist,bptr->dist,sec->lb,accn);
        hptr->time=time_to_crown(hptr->ros,at->rso,accn);
        fptr->time=time_to_crown(fptr->ros,at->rso,accn);
        bptr->time=time_to_crown(bptr->ros,at->rso,accn);
      }
    else
      {
        set_all(hptr,data->time);
        set_all(fptr,data->time);
        set_all(bptr,data->time);
      }
    sec->area=area((hptr->dist+bptr->dist),fptr->dist);
    if(data->pattern==1 && data->time>0) sec->perm=perimeter(hptr,bptr,sec,sec->lbt);
    else sec->perm=perimeter(hptr,bptr,sec,sec->lb);
   }

void setup_const(fuel_coefs *ptr)
 {
    //printf("dlw debug, enter fuel_coefs\n");
/*   fuel type 0 */
   strncpy(ptr->fueltype,"M1 ",3);
   ptr->a=110.0; ptr->b=0.0282; ptr->c=1.5;
   ptr->q=0.80; ptr->bui0=50; ptr->cbh=6; ptr->cfl=0.80;
/*   fuel type 1 */
   ptr++;
   strncpy(ptr->fueltype,"M2 ",3);
   ptr->a=110.0; ptr->b=0.0282; ptr->c=1.5;
   ptr->q=0.80; ptr->bui0=50; ptr->cbh=6; ptr->cfl=0.80;
/*   fuel type 2 */
   ptr++;
   strncpy(ptr->fueltype,"M3 ",3);
   ptr->a=120.0; ptr->b=0.0572; ptr->c=1.4;
   ptr->q=0.80; ptr->bui0=50; ptr->cbh=6; ptr->cfl=0.80;
/*   fuel type 3 */
   ptr++;
   strncpy(ptr->fueltype,"M4 ",3);
   ptr->a=100.0; ptr->b=0.0404; ptr->c=1.48;
   ptr->q=0.80; ptr->bui0=50; ptr->cbh=6; ptr->cfl=0.80;
/*   fuel type 4 */
   ptr++;
   strncpy(ptr->fueltype,"C1 ",3);
   ptr->a=90.0; ptr->b=0.0649; ptr->c=4.5;
   ptr->q=0.90; ptr->bui0=72; ptr->cbh=2; ptr->cfl=0.75;
 /*  fuel type 5 */
   ptr++;
   strncpy(ptr->fueltype,"C2 ",3);
   ptr->a=110.0; ptr->b=0.0282; ptr->c=1.5;
   ptr->q=0.70; ptr->bui0=64; ptr->cbh=3; ptr->cfl=0.80;
/*   fuel type 6 */
   ptr++;
   strncpy(ptr->fueltype,"C3 ",3);
   ptr->a=110.0; ptr->b=0.0444; ptr->c=3.0;
   ptr->q=0.75; ptr->bui0=62; ptr->cbh=8; ptr->cfl=1.15;
/*   fuel type 7 */
   ptr++;
   strncpy(ptr->fueltype,"C4 ",3);
   ptr->a=110.0; ptr->b=0.0293; ptr->c=1.5;
   ptr->q=0.80; ptr->bui0=66; ptr->cbh=4; ptr->cfl=1.20;
 /*  fuel type 8 */
   ptr++;
   strncpy(ptr->fueltype,"C5 ",3);
   ptr->a=30.0; ptr->b=0.0697; ptr->c=4.0;
   ptr->q=0.80; ptr->bui0=56; ptr->cbh=18; ptr->cfl=1.20;
 /*  fuel type 9 */
   ptr++;
   strncpy(ptr->fueltype,"C6 ",3);
   ptr->a=30.0; ptr->b=0.0800; ptr->c=3.0;
   ptr->q=0.80; ptr->bui0=62; ptr->cbh=7; ptr->cfl=1.80;
 /*  fuel type 10 */
   ptr++;
   strncpy(ptr->fueltype,"C7 ",3);
   ptr->a=45.0; ptr->b=0.0305; ptr->c=2.0;
   ptr->q=0.85; ptr->bui0=106; ptr->cbh=10; ptr->cfl=0.50;
 /*  fuel type 11 */
   ptr++;
   strncpy(ptr->fueltype,"D1 ",3);
   ptr->a=30.0; ptr->b=0.0232; ptr->c=1.6;
   ptr->q=0.90; ptr->bui0=32; ptr->cbh=0; ptr->cfl=0.0;
 /*  fuel type 12 */
   ptr++;
   strncpy(ptr->fueltype,"S1 ",3);
   ptr->a=75.0; ptr->b=0.0297; ptr->c=1.3;
   ptr->q=0.75; ptr->bui0=38; ptr->cbh=0; ptr->cfl=0.0;
 /*  fuel type 13 */
   ptr++;
   strncpy(ptr->fueltype,"S2 ",3);
   ptr->a=40.0; ptr->b=0.0438; ptr->c=1.7;
   ptr->q=0.75; ptr->bui0=63; ptr->cbh=0; ptr->cfl=0.0;
 /*  fuel type 14 */
   ptr++;
   strncpy(ptr->fueltype,"S3 ",3);
   ptr->a=55.0; ptr->b=0.0829; ptr->c=3.2;
   ptr->q=0.75; ptr->bui0=31; ptr->cbh=0; ptr->cfl=0.0;
 /*  fuel type 15 */
   ptr++;
   strncpy(ptr->fueltype,"O1a",3);
   ptr->a=190.0; ptr->b=0.0310; ptr->c=1.40;
   ptr->q=1.000; ptr->bui0=01; ptr->cbh=0; ptr->cfl=0.0;
 /*  fuel type 16 */
   ptr++;
   strncpy(ptr->fueltype,"O1b",3);
   ptr->a=250.0; ptr->b=0.0350; ptr->c=1.7;
   ptr->q=1.000; ptr->bui0=1; ptr->cbh=0; ptr->cfl=0.0;
/*  fuel type 17 */
   ptr++;
   strncpy(ptr->fueltype,"D2 ",3);
   ptr->a=6.0; ptr->b=0.0232; ptr->c=1.6;
   ptr->q=0.90; ptr->bui0=32; ptr->cbh=0; ptr->cfl=0.0;

 }

 char get_fueltype_number(fuel_coefs **ptr,char fuel[4])
 {
   int i;
   char cover;
   if(fuel[0]>='a' && fuel[0]<='z') fuel[0]+='A'-'a';
   if(fuel[2]>='A' && fuel[2]<='Z') fuel[2]+='a'-'A';
   for(i=0; i<numfuels && (strncmp((*ptr)->fueltype,fuel,3)!=0); i++)(*ptr)++;

   if(i>=numfuels)
   {
    printf(" %s not a recognizable fuel type\n ",fuel);
    exit(9);
   }
   if(fuel[0]=='C' || fuel[0]=='M')cover='c';
   else cover='n';

   return (cover);
 }

 float ffmc_effect(float ffmc)
 {
   float mc,ff;
   mc=147.2*(101.0-ffmc)/(59.5+ffmc);
   ff=91.9*exp(-0.1386*mc)*(1+pow(mc,5.31)/49300000.0);
   return (ff);
 }

 float rate_of_spread(inputs *inp, fuel_coefs *ptr, main_outs *at)
 {
   float fw,isz,mult,*mu=&mult,rsi  ;
   at->ff=ffmc_effect(inp->ffmc);
   at->raz=inp->waz;
   isz=0.208*at->ff;
   if(inp->ps>0)at->wsv=slope_effect(inp,ptr,at,isz);
   else at->wsv=inp->ws;
   if(at->wsv<40.0)fw=exp(0.05039*at->wsv);
   else fw=12.0*(1.0-exp(-0.0818*(at->wsv-28)));
   at->isi=isz*fw;
   rsi=ros_calc(inp,ptr,at->isi,mu);
   at->rss=rsi*bui_effect(ptr,at,inp->bui);
   return(at->rss);
 }

 float ros_calc(inputs *inp, fuel_coefs *ptr,float isi,float *mult)
 {
   float ros;
   if(strncmp(inp->fueltype,"O1",2)==0)
                return ( grass(ptr, inp->cur ,isi,mult) );
   if(strncmp(inp->fueltype,"M1",2)==0 || strncmp(inp->fueltype,"M2",2)==0)
                return ( mixed_wood(ptr,isi,mult,inp->pc) );
   if(strncmp(inp->fueltype,"M3",2)==0 || strncmp(inp->fueltype,"M4",2)==0)
                return ( dead_fir(ptr,inp->pdf,isi,mult) );
   if(strncmp(inp->fueltype,"D2",2)==0)
                return ( D2_ROS(ptr,isi,inp->bui,mult) );
 /* if all else has fail its a conifer   */
   return ( conifer(ptr,isi,mult));
 }


  float grass(fuel_coefs *ptr,float cur,float isi,float *mult)
  {
    float mu,ros;
    if((float)(cur)>=58.8) mu=0.176 + 0.02*( (float)(cur) - 58.8 ) ;
    else mu=0.005*(exp(0.061*(float)(cur) ) - 1.0) ;
    ros=mu * (ptr->a*pow( (1.0-exp(-1.0*ptr->b*isi)) , ptr->c));
    if(mu<0.001)mu=0.001;  /* to have some value here*/
    *mult=mu;
    return(ros);
  }

  float mixed_wood(fuel_coefs *ptr, float isi,float *mu, int pc)
  {
    float ros, mult,ros_d1,ros_c2;
    int i;
    *mu=pc/100.0;
    ros_c2=ptr->a*pow( (1.0-exp(-1.0*ptr->b*isi)), ptr->c);
    if(strncmp(ptr->fueltype,"M2",2)==0) mult=0.2;
    else mult=1.0;
    for(i=0;strncmp(ptr->fueltype,"D1",2)!=0 && i<numfuels;ptr++,i++);
    if(i>=numfuels) { printf(" prob in mixedwood   d1 not found \n");exit(9);}
    ros_d1=ptr->a*pow( (1.0-exp(-1.0*ptr->b*isi) ),ptr->c);

    ros=(pc/100.0)*ros_c2 + mult* (100-pc)/100.0*ros_d1;
    return(ros);
  }

  float dead_fir(fuel_coefs *ptr, int pdf, float isi, float *mu)
  {
    double a,b,c;
    int i;
    float ros,rosm3or4_max,ros_d1, greenness=1.0;
    if(strncmp(ptr->fueltype,"M4",2)==0)greenness=0.2;

    rosm3or4_max=ptr->a*pow( ( 1.0-exp(-1.0*ptr->b*isi)),ptr->c);

    for(i=0;strncmp(ptr->fueltype,"D1",2)!=0 && i<numfuels;ptr++,i++);
    if(i>=numfuels) { printf(" prob in mixedwood   d1 not found \n");exit(9);}
    ros_d1=ptr->a*pow( (1.0-exp(-1.0*ptr->b*isi) ),ptr->c);

    ros=(float)(pdf)/100.0*rosm3or4_max + (100.0-(float)(pdf))/100.0*greenness*ros_d1;

    *mu=(float)(pdf)/100.0;

    return(ros);
  }

  float D2_ROS(fuel_coefs *ptr, float isi, float bui, float *mu)
  {
    *mu=1.0;
    if(bui>=80) return( ptr->a*pow( (1.0-exp(-1.0*ptr->b*isi) ),ptr->c) );
    else return (0.0);
  }

  float conifer(fuel_coefs *ptr, float isi, float *mu)
  {
    *mu=1.0;
    return( ptr->a*pow( (1.0-exp(-1.0*ptr->b*isi) ),ptr->c) );
  }

  float bui_effect(fuel_coefs *ptr,main_outs *at, float bui)
  {
    float  bui_avg=50.0;

    if(bui==0) bui=1.0;
    at->be=exp(bui_avg*log(ptr->q)*( (1.0/bui)-(1.0/ptr->bui0) ) );
    return (at->be);
  }

  float slope_effect(inputs *inp,fuel_coefs *ptr,main_outs *at, float isi )
  /* ISI is ISZ really */
  {
    double isf,rsf,wse,ps,rsz,wsx,wsy,wsex,wsey,wsvx,wsvy,
        wrad,srad,wsv,raz,check,wse2,wse1;
    float mu=0.0;
    ps=inp->ps*1.0;

    if(ps>70.0)ps=70.0;   /* edited in version 4.6*/
    at->sf=exp(3.533*pow(ps/100.0,1.2));
    if(at->sf>10.0)at->sf=10.00;  /* added to ensure maximum is correct in version 4.6  */

    if(strncmp(ptr->fueltype,"M1",2)==0 || strncmp(ptr->fueltype,"M2",2)==0)
        isf=ISF_mixedwood(ptr,isi,inp->pc,at->sf);
    else if(strncmp(ptr->fueltype,"M3",2)==0 || strncmp(ptr->fueltype,"M4",2)==0)
        isf=ISF_deadfir(ptr,isi,inp->pdf,at->sf);
    else{
     rsz=ros_calc(inp,ptr,isi,&mu);
     rsf=rsz*at->sf;

     if(rsf>0.0)check=1.0-pow((rsf/(mu*ptr->a)),(1.0/ptr->c) );
     else check=1.0;
     if(check<slopelimit_isi)check=slopelimit_isi;

     isf=(1.0/(-1.0*ptr->b))*log(check);
    }
    if(isf==0.0)isf=isi;  /* should this be 0.0001 really  */
    wse1 = log(isf/(0.208*at->ff))/0.05039;
    if(wse1<=40.0) wse=wse1;
    else{
      if(isf>(0.999*2.496*at->ff) ) isf=0.999*2.496*at->ff;
      wse2=28.0-log(1.0-isf/(2.496*at->ff))/0.0818;
      wse=wse2;
    }
    wrad=inp->waz/180.0*3.1415926;
    wsx=inp->ws*sin(wrad);
    wsy=inp->ws*cos(wrad);
    srad=inp->saz/180.0*3.1415926;
    wsex=wse*sin(srad);
    wsey=wse*cos(srad);
    wsvx=wsx+wsex;
    wsvy=wsy+wsey;
    wsv=sqrt(wsvx*wsvx+wsvy*wsvy);
    raz=acos(wsvy/wsv);
    raz=raz/3.1415926*180.0;
    if(wsvx<0)raz=360-raz;
    at->raz=raz;
    return( (float)(wsv) );
  }

 float ISF_mixedwood(fuel_coefs *ptr, float isz, int pc, float sf)
  {
    float check, mult,rsf_d1,rsf_c2,isf_d1,isf_c2;
    int i;

    rsf_c2=sf*ptr->a*pow( (1.0-exp(-1.0*ptr->b*isz)), ptr->c);
    if(rsf_c2>0.0)check=1.0-pow((rsf_c2/(ptr->a)),(1.0/ptr->c) );
    else check=1.0;
    if(check<slopelimit_isi)check=slopelimit_isi;
    isf_c2=(1.0/(-1.0*ptr->b))*log(check);

    if(strncmp(ptr->fueltype,"M2",2)==0) mult=0.2;
    else mult=1.0;
    for(i=0;strncmp(ptr->fueltype,"D1",2)!=0 && i<numfuels;ptr++,i++);
    rsf_d1=sf*(mult*ptr->a)*pow( (1.0-exp(-1.0*ptr->b*isz) ),ptr->c);

    if(rsf_d1>0.0)check=1.0-pow((rsf_d1/(mult*ptr->a)),(1.0/ptr->c) );
    else check=1.0;
    if(check<slopelimit_isi)check=slopelimit_isi;
    isf_d1=(1.0/(-1.0*ptr->b))*log(check);

    return  ( ((float)(pc)/100.0)*isf_c2 + (100-(float)(pc))/100.0*isf_d1  );
  }

 float ISF_deadfir(fuel_coefs *ptr, float isz, int pdf, float sf)
  {
    float check, mult,rsf_d1,rsf_max,isf_d1,isf_max;
    int i;

    rsf_max=sf*ptr->a*pow( (1.0-exp(-1.0*ptr->b*isz)), ptr->c);
    if(rsf_max>0.0)check=1.0-pow((rsf_max/(ptr->a)),(1.0/ptr->c) );
    else check=1.0;
    if(check<slopelimit_isi)check=slopelimit_isi;
    isf_max=(1.0/(-1.0*ptr->b))*log(check);

    if(strncmp(ptr->fueltype,"M4",2)==0) mult=0.2;
    else mult=1.0;

    for(i=0;strncmp(ptr->fueltype,"D1",2)!=0 && i<numfuels;ptr++,i++);
    rsf_d1=sf*(mult*ptr->a)*pow( (1.0-exp(-1.0*ptr->b*isz) ),ptr->c);

    if(rsf_d1>0.0)check=1.0-pow((rsf_d1/(mult*ptr->a)),(1.0/ptr->c) );
    else check=1.0;
    if(check<slopelimit_isi)check=slopelimit_isi;
    isf_d1=(1.0/(-1.0*ptr->b))*log(check);

    return  ( ((float)(pdf)/100.0)*isf_max + ( 100.0-(float)(pdf) )/100.0*isf_d1  );
  }


  float fire_intensity (float fc,float ros)
  {
    return (300.0*fc*ros);
  }

  float foliar_moisture(inputs *inp, main_outs *at)
  {
    float latn;
    int nd;
    at->jd=inp->jd;
    at->jd_min=inp->jd_min;
    if(inp->jd_min<=0)
     {
       if(inp->elev<0)
        {
         latn=23.4*exp(-0.0360*(150-inp->lon))+46.0;
         at->jd_min=(int)(0.5+151.0*inp->lat/latn);
        }
       else
        {
         latn=33.7*exp(-0.0351*(150-inp->lon))+43.0;
         at->jd_min=(int)(0.5+142.1*inp->lat/latn+(0.0172*inp->elev));
        }
     }
    nd=abs(inp->jd - at->jd_min);
    if(nd>=50) return(120.0);
    if(nd>=30 && nd<50) return (32.9+3.17*nd-0.0288*nd*nd);
    return(85.0+0.0189*nd*nd);
  }

  float surf_fuel_consump(inputs *inp)
  {
    float sfc,ffc,wfc,bui,ffmc,sfc_c2,sfc_d1;
    char ft[3];
    strncpy(ft,inp->fueltype,2);
    bui=inp->bui;
    ffmc=inp->ffmc;
    if(strncmp(ft,"C1",2)==0)
     {
/*       sfc=1.5*(1.0-exp(-0.23*(ffmc-81.0)));*/
        if(ffmc>84) sfc=0.75+0.75*sqrt(1-exp(-0.23*(ffmc-84) ));
        else  sfc=0.75-0.75*sqrt(1-exp(0.23*(ffmc-84) ) );
       return (  sfc>=0 ? sfc: 0.0 );
     }
    if(strncmp(ft,"C2",2)==0 || strncmp(ft,"M3",2)==0 ||
            strncmp(ft,"M4",2)==0)return ( 5.0*(1.0-exp(-0.0115*bui)) );
    if(strncmp(ft,"C3",2)==0 || strncmp(ft,"C4",2)==0)
        return( 5.0 * pow( (1.0-exp(-0.0164*bui)) , 2.24));
    if(strncmp(ft,"C5",2)==0 || strncmp(ft,"C6",2)==0 )
        return( 5.0* pow( (1.0-exp(-0.0149*bui)) , 2.48) );
    if(strncmp(ft,"C7",2)==0)
     {
      ffc=2.0*(1.0-exp(-0.104*(ffmc-70.0)));
      if(ffc<0) ffc=0.0;
      wfc=1.5*(1.0-exp(-0.0201*bui));
      return( ffc + wfc );
     }
    if(strncmp(ft,"O1",2)==0) return( (inp->gfl) /* change this*/ );
    if(strncmp(ft,"M1",2)==0 || strncmp(ft,"M2",2)==0)
     {
      sfc_c2=5.0*(1.0-exp(-0.0115*bui));
      sfc_d1=1.5*(1.0-exp(-0.0183*bui));
      sfc=inp->pc/100.0*sfc_c2 + (100.0-inp->pc)/100.0*sfc_d1;
      return(sfc);
     }
    if(strncmp(ft,"S1",2)==0)
     {
      ffc=4.0 * (1.0-exp(-0.025*bui));
      wfc=4.0*(1.0-exp(-0.034*bui));
      return ( ffc+wfc);
     }
    if(strncmp(ft,"S2",2)==0)
     {
      ffc=10.0*(1.0-exp(-0.013*bui));
      wfc=6.0*(1.0-exp(-0.060*bui));
      return (ffc+wfc);
     }
    if(strncmp(ft,"S3",2)==0)
     {
      ffc=12.0*(1.0-exp(-0.0166*bui));
      wfc=20.0*(1.0-exp(-0.0210*bui));
      return ( ffc+wfc);
     }
    if(strncmp(ft,"D1",2)==0) return ( 1.5*(1.0-exp(-0.0183*bui)));
    if(strncmp(ft,"D2",2)==0) return ( bui>=80 ? 1.5*(1.0-exp(-0.0183*bui)) : 0.0);

    printf("prob in sfc func \n");exit(9);
    return(-99);
  }


  float crit_surf_intensity(fuel_coefs *ptr, float fmc)
  {

   return ( 0.001*pow(ptr->cbh*(460.0+25.9*fmc),1.5) );
  }

  float critical_ros(char ft[3],float sfc,float csi)
  {
      if(sfc>0)return ( csi/(300.0*sfc) );
      else return(0.0);
  }

  float crown_frac_burn(float rss,float rso)
  {
   float cfb;
   cfb=1.0-exp(-0.230*(rss-rso));
   return (  cfb>0 ? cfb :0.0 );
  }

  char fire_type( float csi,float sfi)
  {
   return ( sfi>csi ? 'c' : 's' );
  }

  char fire_description(float cfb)
  {
    if(cfb<0.1)return('S');
    if(cfb<0.9 && cfb>=0.1)return('I');
    if(cfb>=0.9)return( 'C' );
    return('*');
  }

  float final_ros(inputs *inp, float fmc,float isi,float cfb,float rss)
  {
    float rsc,ros;
    if(strncmp(inp->fueltype,"C6",2)==0)
    {
     rsc=foliar_mois_effect(isi,fmc);
     ros = rss+cfb*(rsc-rss);
    }
    else ros=rss;
    return(ros);
  }

  float foliar_mois_effect(float isi,float fmc)
  {
    float fme,rsc, fme_avg = 0.778;
    fme=1000.0*pow(1.5-0.00275*fmc,4.0)/(460.0 + 25.9*fmc);
    rsc=60.0*(1.0-exp(-0.0497*isi))*fme/fme_avg;
    return(rsc);
  }

  float crown_consump(inputs *inp, fuel_coefs *ptr,float cfb)
  {
   float cfc;
   cfc=ptr->cfl*cfb;
   if(strncmp(inp->fueltype,"M1",2)==0 || strncmp(inp->fueltype,"M2",2)==0)
         cfc = inp->pc/100.0*cfc;
   if(strncmp(inp->fueltype,"M3",2)==0 || strncmp(inp->fueltype,"M4",2)==0)
         cfc = inp->pdf/100.0*cfc;
   return(cfc);
  }


  float l_to_b(char ft[3],float ws)
  {
    if(strncmp(ft,"O1",2)==0)return( ws<1.0 ? 1.0 : (1.1*pow(ws,0.464)));
    else  return (1.0 +8.729*pow(1.0-exp(-0.030*ws),2.155));
  }

  void set_all (fire_struc *ptr, int time)
  {
     ptr->time=0;
     ptr->rost=ptr->ros;
     ptr->dist=time*ptr->ros;
  }
  float backfire_isi(main_outs *at)
  {
    float bfw;
    bfw = exp(-0.05039*at->wsv);
    return ( 0.208*at->ff*bfw);
  }

  float backfire_ros(inputs *inp,fuel_coefs *ptr,main_outs *at,float bisi)
  {
    float mult=0.0,bros;
    bros=ros_calc(inp,ptr,bisi,&mult);
    bros *= bui_effect(ptr,at,inp->bui);
    return(bros);
  }

  float area(float dt,float df)
  {
    float a,b;
    a=dt/2.0;
    b=df;
    return ( a*b*3.1415926/10000.0);
  }

  float perimeter (fire_struc *h,fire_struc *b, snd_outs *sec, float lb)
  {
    float mult,p;
    mult=3.1415926*(1.0+1.0/lb)*(1.0+pow(((lb-1.0)/(2.0*(lb+1.0))),2.0));
    p=(h->dist + b->dist)/2.0*mult;
    sec->pgr = (h->rost + b->rost)/2.0*mult;

    return(p);
  }

  float acceleration(inputs *inp,float cfb)
  {
    int i;
    char canopy='c',
     open_list[10][3]={"O1","C1","S1","S2","S3","o1","c1","s1","s2","s3"};
    for(i=0;strncmp(inp->fueltype,open_list[i],2)!=0 && i<10;i++);
    if(i<10) canopy='o';
    if(canopy=='o') return(0.115);
    else return(0.115 -18.8*pow(cfb,2.5)*exp(-8.0*cfb) );
  }

  float flankfire_ros(float ros,float bros,float lb)
   {
      return  ( (ros+bros)/(lb*2.0) );
    }

  float flank_spread_distance(inputs *inp,fire_struc *ptr,snd_outs *sec,
      float hrost,float brost,float hd, float bd,float lb,float a)
  {
    sec->lbt=(lb-1.0)*(1.0-exp(-a*inp->time)) +1.0;
    ptr->rost=(hrost+brost)/(sec->lbt*2.0);
    return ( (hd+bd)/(2.0*sec->lbt) );
  }

  float spread_distance(inputs *inp,fire_struc *ptr,float a)
  {
    ptr->rost= ptr->ros*(1.0-exp(-a*inp->time));
    return ( ptr->ros*(inp->time+(exp(-a*inp->time)/a)-1.0/a));
  }

  int time_to_crown(float ros,float rso,float a)
  {
    float ratio;
    if(ros>0)ratio= rso/ros; 
    else ratio=1.1;
    if(ratio>0.9 && ratio<=1.0 )ratio=0.9;
    if(ratio<1.0)return (int)(log(1.0-ratio)/-a);
    else return(99);
  }

  float fire_behaviour(inputs *inp,fuel_coefs *ptr,main_outs *at,
                             fire_struc *f)
  {
    float sfi,fi;
    char firetype;
    sfi=fire_intensity(at->sfc,f->rss);
    firetype=fire_type(at->csi,sfi);
    if(firetype=='c')
     {
       f->cfb = crown_frac_burn(f->rss,at->rso);
       f->fd = fire_description(f->cfb);
       f->ros = final_ros(inp,at->fmc,f->isi,f->cfb,f->rss);
       f->cfc = crown_consump(inp,ptr,f->cfb);
       f->fc = f->cfc + at->sfc;
       fi = fire_intensity(f->fc,f->ros);
     }
    if(firetype!='c' || at->covertype=='n')
     {
       f->fc = at->sfc;
       fi = sfi;
       f->cfb=0.0;
       f->fd='S';
       f->ros=f->rss;
     }
    return(fi);
  }

  float flank_fire_behaviour(inputs *inp,fuel_coefs *ptr,main_outs *at,
                             fire_struc *f)
  {
    float sfi,fi;
    char firetype;
    sfi=fire_intensity(at->sfc,f->rss);
    firetype=fire_type(at->csi,sfi);
    if(firetype=='c')
     {
       f->cfb = crown_frac_burn(f->rss,at->rso);
       f->fd = fire_description(f->cfb);
       f->cfc = crown_consump(inp,ptr,f->cfb);
       f->fc = f->cfc + at->sfc;
       fi = fire_intensity(f->fc,f->ros);
     }
    if(firetype!='c' || at->covertype=='n')
     {
       f->fc = at->sfc;
       fi = sfi;
       f->cfb=0.0;
       f->fd='S';
    /*   f->ros=f->rss;  removed...v4.5   should not have been here ros set in flankfire_ros()  */
     }
    return(fi);
  }


  void zero_main(main_outs *m)
  {
    //printf("dlw debug, enter zero_main\n");
    m->sfc=0.0;
    //printf("dlw debug, completed sfc zero assign\n");
    m->csi=0.0;m->rso=0.0;m->fmc=0;m->sfi=0.0;
    m->rss=0.0;m->isi=0.0;m->be=0.0;m->sf=1.0;m->raz=0.0;m->wsv=0.0;
    m->ff=0.0; m->jd=0;m->jd_min=0;
    m->covertype=' ';
  }

  void zero_sec (snd_outs *s)
  {
    //printf("dlw debug, enter zero_sec\n");
    //printf("dlw debug, trying s->lb=%f\n",s->lb);
    s->lb=0.0;
    //printf("dlw debug, completed s->lb=0.0\n"); 
    s->area=0.0;
    //printf("dlw debug, completed s->area=0.0\n"); 
    s->perm=0.0;
    //printf("dlw debug, completed s->perm=0.0\n"); 
    s->pgr=0.0;
    //printf("dlw debug, completed s->pgr=0.0\n"); 
  }

  void zero_fire (fire_struc *a)
  {
    //printf("dlw debug, enter zero_fire\n");
    //printf("try before assign a->ros=%f\n", a->ros);
    a->ros=0.0;
    //printf("dlw debug, did a->ros\n"); 
    a->dist=0.0;a->rost=0.0;a->cfb=0.0;a->fi=0.0;
    //printf("dlw debug, did a->fi\n"); 
    a->fc=0.0;a->cfc=0.0;a->time=0.0;
    //printf("dlw debug, did a->time\n"); 
  }