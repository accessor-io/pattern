
#include <stdio.h>
#include <stdlib.h>
#include <math.h>


typedef struct tree {
  int data;
  int max_path;
  struct tree *lparent;
  struct tree *rparent;
} Tree;


#define HEIGHT 100
#define LENGTH (HEIGHT * (HEIGHT + 1)) / 2

#define POS(x, y) ((y) * ((y) + 1) / 2 + (x))

int main(void) {
  Tree *list[LENGTH];

  FILE *fh   = fopen("67.data", "r");
  char buffer[1048];
  char *data;
  int i, j, max;


 /* Allocate tree */
  for(i = 0; i < LENGTH; ++i) {
    list[i] = malloc(sizeof *list[i]);
    if(list[i] == NULL) {
      puts("Shit. Outta RAM.");
      exit(EXIT_FAILURE);
    }
  }
 /* Link up tree */
  for(i = 0; i < HEIGHT; ++i) {
    for(j = 0; j <= i; ++j) {
      if(j > 0)
        list[POS(j, i)]->lparent = list[POS(j - 1, i - 1)];
      if(j < i)
        list[POS(j, i)]->rparent = list[POS(j,     i - 1)];
    }
  }

 /* Populate tree */
  i = 0;
  while(fgets(buffer, sizeof buffer, fh)) {
    data = buffer;

    while(*data != '\n') {
      list[i]->data = strtoul(data, &data, 10);
      ++i;
    }
  }

 /* Traverse tree, calculate maximum depths */
  list[0]->max_path = list[0]->data;
  for(i = 1; i < LENGTH; ++i) {
    if(list[i]->lparent == NULL &&
       list[i]->rparent != NULL)
      list[i]->max_path = list[i]->data + list[i]->rparent->max_path;
    else if(list[i]->lparent != NULL &&
       list[i]->rparent == NULL)
      list[i]->max_path = list[i]->data + list[i]->lparent->max_path;
    else if(list[i]->lparent != NULL &&
            list[i]->rparent != NULL) {
      if(list[i]->lparent->max_path > list[i]->rparent->max_path)
        list[i]->max_path = list[i]->data + list[i]->lparent->max_path;
      else
        list[i]->max_path = list[i]->data + list[i]->rparent->max_path;
    }
  }
 /* Done! Check last row for maximum value */
  max = 0;
  for(i = LENGTH - HEIGHT - 1; i < LENGTH; ++i) {
    if(list[i]->max_path > max)
      max = list[i]->max_path;
  }

  printf("Max: %d\n", max);

  fclose(fh);
  return 0;
}

