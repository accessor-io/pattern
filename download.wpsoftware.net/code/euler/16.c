
#include <stdio.h>

/* 32-bit digits (though I'm using a 64-bit type to
   facilitate long division  */
unsigned long n[32] = { 1 << 8 };

/* returns remainder */
int div_10() {
  unsigned long r, i;

  for(i = 0; i < 31; ++i) {
    r = n[i] % 10;
    n[i] /= 10;
    n[i + 1] += (r << 32);
  }
  r = n[31] % 10;
  n[31] /= 10;

  return r;
}

int main(void) {
  int i, sum;

  for(i = 0; i < 400; ++i)
    sum += div_10();

  printf("Sum: %d\n", sum);

  return 0;
}





