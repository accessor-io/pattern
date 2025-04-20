# Transaction Relationship Diagram

Below is a Mermaid diagram visualizing the relationship between the two transactions present in the JSON file.

```mermaid
graph TD;
    TX_08389f34["Transaction: 08389f34...\n(Parent Transaction)\nBlock: 339085\nBlock Time: 1421345234\nFee: 400000\nOutput[32]: 3300000"]
    TX_718f79["Transaction: 718f79...\n(Spending Transaction)\nBlock: 339226\nBlock Time: 1421426608\nFee: 20000\nReceived: 3280000"]

    TX_08389f34 -->|"Provides input (output index 32) to"| TX_718f79
```

*Notes:*
- Transaction "08389f34..." is the parent transaction containing many outputs, with its output at index 32 (3300000 satoshis) used as an input in the spending transaction.
- Transaction "718f79..." receives 3280000 satoshis after accounting for a fee of 20000 satoshis.
- Data is extracted from tx_cache/187swFMjz1G54ycVU56B7jZFHFTNVQFDiu.json. 