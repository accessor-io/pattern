/*
 * Andrew Poelstra, December 2011
 * This code is public domain.
 */

#include <stdio.h>

#define NUM_PARTS	3	/* use 3-partitions */
#define MAX_SIZE	32	/* maximum size of a part, make this big */

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

/* Predict the next sequence element for each partition */
void predict_next_sequence(Part *p)
{
  unsigned i;
  printf("Predicted next elements:\n");
  for (i = 0; i < NUM_PARTS; ++i)
  {
    if (p->size[i] >= 2)
    {
      unsigned last = p->seq[i][p->size[i]];
      unsigned second_last = p->seq[i][p->size[i] - 1];
      unsigned predicted = last + (last - second_last);
      printf("Partition %d: %d\n", i + 1, predicted);
    }
    else
    {
      printf("Partition %d: Not enough data to predict\n", i + 1);
    }
  }
}

int main(void)
{
  /* Seed partition -- note that all parts must start with a
   * dummy (I have chosen zero) since C 0-indexes its arrays
   * but my algorithm 1-indexes them. */
  Part p = { /* Partition */
             {1L, 3L, 8L, 21L, 49L, 76L, 224L, 467L, 514L, 1155L, 2683L, 5216L, 10544L, 26867L, 51510L, 95823L, 198669L, 357535L, 863317L, 1811764L, 3007503L, 5598802L, 14428676L, 33185509L, 54538862L, 111949941L, 227634408L, 400708894L, 1033162084L, 2102388551L, 3093472814L, 7137437912L, 14133072157L, 20112871792L, 42387769980L, 100251560595L, 146971536592L, 323724968937L, 1003651412950L, 1458252205147L, 2895374552463L, 7409811047825L, 15404761757071L, 19996463086597L, 51408670348612L, 119666659114170L, 191206974700443L, 409118905032525L, 611140496167764L, 2058769515153876L, 4216495639600700L, 6763683971478124L, 9974455244496707L, 30045390491869460L, 44218742292676575L, 138245758910846492L, 199976667976342049L, 525070384258266191L, 1135041350219496382L, 1425787542618654982L, 3908372542507822062L, 8993229949524469768L, 17799667357578236628L, 30568377312064202855L, 46346217550346335726L},
             /* Sizes */
             {64}};
  /* Predict the next sequence */
  predict_next_sequence(&p);
  return 0;
}

