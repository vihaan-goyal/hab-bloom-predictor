// loop_test.cpp -- PC harness for loop_control.h, driven by check_loop_port.py.
// stdin:  "c <tOn> <cOk> <warm|nan> <floorFrac> <X> <maxOn> <mode>"   starts a new scenario
//         "d <day> <p|nan> <chl|nan> <stop 0|1>"                      one day
// stdout: "<label> <next_check|-> <episodes>" per day
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "loop_control.h"

static float val(const char *s) { return (!strcmp(s, "nan") || !strcmp(s, "-")) ? NAN : strtof(s, NULL); }

int main() {
  LoopCfg c; LoopState s;
  loop_defaults(c, 0.5f); loop_reset(s);
  char line[256], a[32], b[32], d[32], e[32], f[32], g[32], h[32];
  while (fgets(line, sizeof(line), stdin)) {
    if (line[0] == 'c') {
      sscanf(line + 1, "%31s %31s %31s %31s %31s %31s %31s", a, b, d, e, f, g, h);
      loop_defaults(c, val(a)); loop_reset(s);
      c.cOk = val(b); c.warmMean = val(d); c.floorFrac = val(e); c.X = atoi(f); c.maxOnDays = atoi(g); c.mode = h[0];
    } else if (line[0] == 'd') {
      int stop = 0;
      sscanf(line + 1, "%31s %31s %31s %d", a, b, d, &stop);
      bool was = s.on;
      if (stop) s.safetyStop = true;
      LoopOut o = loop_step(c, s, atoi(a), val(b), val(d));
      if (s.on) printf("%s %ld %ld\n", loop_label(s, o, was), (long)s.checkDay, (long)s.episodes);
      else printf("%s - %ld\n", loop_label(s, o, was), (long)s.episodes);
    }
  }
  return 0;
}
