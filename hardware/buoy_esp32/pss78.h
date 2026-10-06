/* pss78.h -- practical salinity from conductivity + temperature (PSS-78, UNESCO 1983)
   ===================================================================================
   S = sum a_i Rt^(i/2) + dT/(1 + k dT) * sum b_i Rt^(i/2),  dT = t68 - 15,  k = 0.0162
   Rt = R / (Rp * rt),  R = C / C(35, 15, 0) with C(35,15,0) = 42.914 mS/cm
   rt = c0 + c1 t + c2 t^2 + c3 t^3 + c4 t^4
   Rp = 1 + p (e1 + e2 p + e3 p^2) / (1 + d1 t + d2 t^2 + R (d3 + d4 t))
   Temperatures in the formula are IPTS-68; sensors report ITS-90, so t68 = 1.00024 t90.
   Valid for 2 <= S <= 42 and -2 <= t <= 35 C.

   Reference check (UNESCO Tech. Pap. Mar. Sci. 44, 1983; run by `selftest`):
     R = 1,        t68 = 15 C, p = 0         ->  S = 35.0000  (C = 42.914 mS/cm, definition)
     R = 1.888091, t68 = 40 C, p = 10000 dbar ->  S = 40.0000  (the published check value)
   A buoy at the surface passes p = 0.
*/
#ifndef BUOY_PSS78_H
#define BUOY_PSS78_H
#include <math.h>

#define PSS78_C35 42.914   // mS/cm, conductivity of standard seawater S=35 at 15 C (IPTS-68), p=0

static double pss78_salinity(double cond_mScm, double t90, double p_dbar) {
  if (isnan(cond_mScm) || isnan(t90) || isnan(p_dbar) || cond_mScm <= 0) return NAN;
  static const double a[6] = {0.0080, -0.1692, 25.3851, 14.0941, -7.0261, 2.7081};
  static const double b[6] = {0.0005, -0.0056, -0.0066, -0.0375, 0.0636, -0.0144};
  static const double c[5] = {0.6766097, 2.00564e-2, 1.104259e-4, -6.9698e-7, 1.0031e-9};
  const double d1 = 3.426e-2, d2 = 4.464e-4, d3 = 4.215e-1, d4 = -3.107e-3;
  const double e1 = 2.070e-5, e2 = -6.370e-10, e3 = 3.989e-15, k = 0.0162;
  double t = 1.00024 * t90, p = p_dbar;
  double R = cond_mScm / PSS78_C35;
  double rt = c[0] + t * (c[1] + t * (c[2] + t * (c[3] + t * c[4])));
  double Rp = 1.0 + p * (e1 + p * (e2 + p * e3)) / (1.0 + d1 * t + d2 * t * t + R * (d3 + d4 * t));
  double Rt = R / (Rp * rt);
  if (Rt <= 0) return NAN;
  double sr = sqrt(Rt), dT = t - 15.0;
  double sa = 0, sb = 0, pw = 1;
  for (int i = 0; i < 6; i++) { sa += a[i] * pw; sb += b[i] * pw; pw *= sr; }
  return sa + dT / (1.0 + k * dT) * sb;
}
#endif
