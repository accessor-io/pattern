#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

#define NUM_PARTS 160
#define MAX_SIZE 1024
#define HEX_STR_SIZE 65  // 64 chars + null terminator

// 256-bit number representation
typedef struct {
    uint64_t parts[4];  // For 256-bit numbers
} big_num;

typedef struct {
    big_num seq[NUM_PARTS][MAX_SIZE];
    unsigned size[NUM_PARTS];
} HexPart;

// Convert hex string to big_num
big_num hex_to_bignum(const char *hex) {
    big_num result = {0};
    char chunk[17];  // 16 chars + null terminator
    
    // Process 16 chars (64 bits) at a time
    for(int i = 0; i < 4; i++) {
        strncpy(chunk, hex + i*16, 16);
        chunk[16] = '\0';
        sscanf(chunk, "%16lx", &result.parts[3-i]);
    }
    return result;
}

// Check if three big_nums form an arithmetic progression
int is_arithmetic_progression(big_num a, big_num b, big_num c) {
    // Check if b-a == c-b for each part
    for(int i = 0; i < 4; i++) {
        if((b.parts[i] - a.parts[i]) != (c.parts[i] - b.parts[i])) {
            return 0;
        }
    }
    return 1;
}

void print_bignum(big_num n) {
    printf("%016lx%016lx%016lx%016lx", 
           n.parts[0], n.parts[1], n.parts[2], n.parts[3]);
}

int check_hex_part(HexPart *p) {
    int valid = 1;
    #pragma omp parallel for reduction(&:valid)
    for(int n = 0; n < NUM_PARTS; n++) {
        for(int i = 0; i < p->size[n]-2 && valid; i++) {
            for(int j = i+1; j < p->size[n]-1 && valid; j++) {
                for(int k = j+1; k < p->size[n] && valid; k++) {
                    if(is_arithmetic_progression(
                        p->seq[n][i], p->seq[n][j], p->seq[n][k])) {
                        valid = 0;
                        break;
                    }
                }
            }
        }
    }
    return valid;
}

void analyze_hex_sequence(const char* filename) {
    FILE *f = fopen(filename, "r");
    if(!f) {
        printf("Could not open file: %s\n", filename);
        return;
    }

    HexPart p = {0};
    char line[HEX_STR_SIZE];
    int total = 0;

    // Read hex numbers
    while(fgets(line, sizeof(line), f) && total < MAX_SIZE) {
        line[64] = '\0';  // Ensure string is terminated
        big_num num = hex_to_bignum(line);
        
        // Try to add to each partition
        for(int i = 0; i < NUM_PARTS; i++) {
            p.seq[i][p.size[i]] = num;
            p.size[i]++;
            
            if(check_hex_part(&p)) {
                // Valid partition found
                printf("Added number to partition %d:\n", i);
                print_bignum(num);
                printf("\n");
                total++;
                break;
            }
            // Undo if not valid
            p.size[i]--;
        }
    }

    fclose(f);
    
    // Print results
    printf("\nPartition Analysis Results:\n");
    for(int i = 0; i < NUM_PARTS; i++) {
        if(p.size[i] > 0) {
            printf("Partition %d size: %d\n", i, p.size[i]);
        }
    }
}

int main(int argc, char **argv) {
    if(argc != 2) {
        printf("Usage: %s <hex_file>\n", argv[0]);
        return 1;
    }
    
    analyze_hex_sequence(argv[1]);
    return 0;
} 