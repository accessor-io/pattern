#include <stdio.h>
#include <omp.h>

#define NUM_PARTS 128
#define MAX_SIZE 32
typedef struct part {
    unsigned seq[NUM_PARTS][MAX_SIZE];
    unsigned size[NUM_PARTS];
} Part;

void print_part(Part *p) {
    unsigned i, j;
    puts("Partition Summary:");
    printf("Total partitions: %d\n", NUM_PARTS);
    printf("Non-empty partitions:\n");
    for (i = 0; i < NUM_PARTS; ++i) {
        if (p->size[i] > 0) {
            printf("Partition %3d [size=%d]: ", i, p->size[i]);
            if (p->size[i] > 10) {
                for (j = 1; j <= 5; ++j) printf("%d, ", p->seq[i][j]);
                printf("... ");
                for (j = p->size[i]-4; j <= p->size[i]; ++j) 
                    printf("%d, ", p->seq[i][j]);
            } else {
                for (j = 1; j <= p->size[i]; ++j) 
                    printf("%d, ", p->seq[i][j]);
            }
            printf("\n");
        }
    }
}

int check_part(Part *p) {
    int valid = 1;
    #pragma omp parallel for reduction(&:valid)
    for (int n = 0; n < NUM_PARTS; ++n) {
        for (int i = 1 + !(p->size[n] % 2); i < p->size[n] && valid; i += 2) {
            if (2 * p->seq[n][(i + p->size[n])/2] == 
                p->seq[n][i] + p->seq[n][p->size[n]]) {
                valid = 0;
            }
        }
    }
    return valid;
}

void backtrack(Part *p) {
    static unsigned max_len = 0;
    unsigned next = 1;
    int n;
    
    if (check_part(p) == 0) return;

    for (n = 0; n < NUM_PARTS; ++n) {
        next += p->size[n];
    }

    if (next > max_len) {
        max_len = next;
        if (max_len % 10 == 0) {
            printf("New maximum length %d\n", max_len - 1);
            print_part(p);
        }
    }

    for (n = 0; n < NUM_PARTS; ++n) {
        if (p->size[n] < MAX_SIZE - 1) {
            ++p->size[n];
            p->seq[n][p->size[n]] = next;
            backtrack(p);
            --p->size[n];
        }
    }
}

int main(void) {
    Part p = {0};  // Initialize all to 0
    
    // Initialize first few values in each partition
    for (int i = 0; i < NUM_PARTS; i++) {
        p.seq[i][0] = 0;
        p.seq[i][1] = i + 1;
        p.size[i] = 1;
    }
    
    printf("Starting backtracking with %d partitions...\n", NUM_PARTS);
    backtrack(&p);
    return 0;
} 