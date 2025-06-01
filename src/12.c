
#include <stdio.h>

unsigned phi(unsigned n) {
  unsigned rv = 1;  /* Add 1 since we don't count n as a divisor below */
  unsigned i;

  for(i = 1; i < n; ++i)
    if((n % i) == 0)
      ++rv;
  return rv;
}

#define SUMTO(n) ((n) * ((n) + 1) / 2)

int main(void) {
  unsigned n, f;
  unsigned max = 0;

  for(n = 2; max < 500; ++n) {
    /* We know n to be relatively prime to n + 1, so we can simply multiply
     * the phi values together (dividing the appropriate factor by 2) and check
     * if we exceed 500.
     */
    if(n & 1)  f = phi(n) * phi((n + 1) / 2);
    else       f = phi(n / 2) * phi(n + 1);

    if(f > max)
      max = f;
  }
  printf("DONE. Triangle #%u is %u, which has %u factors.\n", n, SUMTO(n), max);
  return 0;
}

