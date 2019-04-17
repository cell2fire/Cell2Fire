/*  fbp.h  -- header file for fbp program  bmw
  function prototypes and structures for fbp.c prog
   nov/92
  modified for version 4.3 of the code
   Aug/2005 bmw
  modified for version 4.5 of the code
   Nov/2007 bmw
   change of name for 5.0
*/

#if !defined(_FBPHEAD)
#define _FBPHEAD

#include <stdio.h>

 typedef struct
   { char fueltype[4];
     float ffmc,ws,gfl,bui,lat,lon;
     int time,pattern,mon,jd,jd_min,waz,ps,saz,pc,
          pdf,cur,elev,hour,hourly;
   } inputs;

typedef struct
  { char fueltype[4];
    float q,bui0,cbh,cfl;
    double a,b,c;
  } fuel_coefs;
  
 typedef struct
  { float ros,dist,rost,cfb,fc,cfc,time,rss,isi;
    char fd;
    double fi;
  }fire_struc;

 typedef struct
  {  float hffmc,sfc,csi,rso,fmc,sfi,rss,isi,be,sf,raz,wsv,ff;
     int jd_min,jd;
     char covertype;
  } main_outs;

 typedef struct
  { float lb,area,perm,pgr,lbt;
  } snd_outs;



float grass(fuel_coefs *ptr,float cur,float isi,float *mu);

float mixed_wood(fuel_coefs *ptr,float isi, float *mult,int pc);

 float ISF_mixedwood(fuel_coefs *ptr, float isz, int pc, float sf);

 float ISF_deadfir(fuel_coefs *ptr, float isz, int pdf, float sf);

float dead_fir(fuel_coefs *ptr,int pdf,float isi,float *mult);

float D2_ROS(fuel_coefs *ptr, float isi, float bui, float *mu);

float conifer(fuel_coefs *ptr,float isi,float *mult);

float bui_effect(fuel_coefs *ptr,main_outs *at, float bui);

float ros_calc(inputs *inp, fuel_coefs *ptr, float isi, float *mu);

float rate_of_spread(inputs *inp,fuel_coefs *ptr, main_outs *at);

float slope_effect(inputs *inp, fuel_coefs *ptr, main_outs *at,float isi);

float surf_fuel_consump(inputs *inp);

float fire_intensity(float fc,float ros);

void setup_const(fuel_coefs *ptr);

char get_fueltype_number(fuel_coefs **ptr,char ft[4]);

float foliar_moisture(inputs *inp, main_outs *at);

float crit_surf_intensity(fuel_coefs *ptr,float fmc);

float critical_ros(char ft[3],float sfc,float csi);

char fire_type(float csi,float sfi);

float crown_frac_burn(float ros,float rso);

char fire_description(float cfb);

float final_ros(inputs *inp, float fmc,float isi,float cfb,float rss);

float crown_consump(inputs *inp, fuel_coefs *ptr, float cfb);

float foliar_mois_effect(float isi,float fmc);

float l_to_b(char ft[3],float ws);

float ffmc_effect(float ffmc);

float backfire_ros(inputs *inp,fuel_coefs *ptr, main_outs *at,float bisi);

float backfire_isi(main_outs *at);

float area(float dt,float df);

float perimeter(fire_struc *h,fire_struc *b,snd_outs *sec,float lb);

float acceleration(inputs *inp, float cfb);

float flankfire_ros(float ros,float bros,float lb);

float spread_distance(inputs *inp, fire_struc *ptr, float accn);

float flank_spread_distance(inputs *inp,fire_struc *ptr, snd_outs *sec,
      float hrost,float brost,float hd, float bd,float lb,float a);

int time_to_crown(float ros,float rso,float a);

float fire_behaviour(inputs *inp,fuel_coefs *ptr,main_outs *at,
                                                    fire_struc *f);
float flank_fire_behaviour(inputs *inp,fuel_coefs *ptr,main_outs *at,
                             fire_struc *f);

void set_all(fire_struc *ptr, int time);

void calculate(inputs *data,fuel_coefs *ptr,main_outs *at,
      snd_outs *sec,fire_struc *hptr,fire_struc *fptr,fire_struc *bptr);

void zero_main(main_outs *m);

void zero_sec (snd_outs *s);

void zero_fire(fire_struc *a);

#endif
