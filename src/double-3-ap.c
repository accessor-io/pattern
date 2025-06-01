/*
 * Andrew Poelstra, December 2011
 * This code is public domain.
 */

#include <stdio.h>

#define NUM_PARTS	3	/* use 3-partitions */
#define MAX_SIZE	1024	/* maximum size of a part, make this big */

/* Partition structure -- WARNING can be overflowed */
typedef struct part
{
  unsigned seq[NUM_PARTS][MAX_SIZE];
  unsigned size[NUM_PARTS];
} Part;

/* Output partition in human-readable format */
void print_part (Part *p)
{
  unsigned i, j;
  puts ("Partition:");
  for (i = 0; i < NUM_PARTS; ++i)
    {
      printf ("[ %d", p->seq[i][1]);
      for (j = 2; j <= p->size[i]; ++j)
        printf (", %d", p->seq[i][j]);
      puts ("]");
    }
}

/* Scan partition for double-3-APs which include the last element
 *  (since we would have caught ones that don't in an earlier step)
 *  Returns 0 if it finds one, 1 if it doesn't. */
int check_part (Part *p)
{
  unsigned n, i;
  for (n = 0; n < NUM_PARTS; ++n)
    for (i = 1 + !(p->size[n] % 2); i < p->size[n]; i += 2)
      if (2 * p->seq[n][(i + p->size[n])/2] == p->seq[n][i] + p->seq[n][p->size[n]])
        return 0;
  return 1;
}

/* Backtrack algorithm */
void backtrack (Part *p)
{
  static unsigned max_len = 0;
  unsigned next = 1;
  int n;

  /* Quit if we don't have a valid partition; adding
   *  more numbers won't ever get us a valid one. */
  if (check_part(p) == 0)
    return;

  /* Get next integer to add */
  for (n = 0; n < NUM_PARTS; ++n)
    next += p->size[n];

  /* Output if this is higher than our old maximum */
  if (next > max_len)
  {
    max_len = next;
    printf ("Got new maximum length %d\n", max_len - 1);
    print_part (p);
  }

  /* Recurse */
  for (n = 0; n < NUM_PARTS; ++n)
    {
      ++p->size[n];
      p->seq[n][p->size[n]] = next;
      backtrack (p);
      --p->size[n];
     }
}


int main(void)
{
  /* Seed partition -- note that all parts must start with a
   * dummy (I have chosen zero) since C 0-indexes its arrays
   * but my algorithm 1-indexes them. */
  Part p = { /* Partition */
             {{0, 5, 8, 9, 14, 15, 17, 18, 21, 22, 27, 30 },
              {0, 1, 3, 4, 12, 19, 20, 24, 26, 31, 33, 34 },
              {0, 2, 6, 7, 10, 11, 13, 16, 23, 25, 28, 29, 32 }},
             /* Sizes */
             {11, 11, 12}};
  /* Go! */
  backtrack (&p);
  return 0;
}

