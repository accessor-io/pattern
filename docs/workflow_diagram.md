# Cryptographic Key Analysis System Workflow Diagram

This diagram outlines how the various components interact within the system.

```mermaid
flowchart TD
    subgraph Input and Preprocessing
        A[Cryptographic Keys (hex values)]
    end

    subgraph Core ASCII Analysis
        B[Convert Keys to ASCII]
        C[Generate Hex Pattern Visualization]
        D[Calculate Metrics
           - % Printable Bytes
           - Printable Streaks
           - Position Heatmap]
    end

    subgraph Extended Analysis
        E[XOR Correlation Engine
           - Validate ASCII via XOR
           - Flag Known Delimiters
           - Hamming Distance]
        F[Temporal Progression Tracking
           - Pattern Evolution
           - Frequency Mapping
           - Byte Position Trends]
        G[Hexdump Visualization
           - Per-key Hex/ASCII Views
           - Color Coding for Control, Alphanumerics, Symbols]
    end

    subgraph Automation & Testing
        H[CI/CD Pipeline
           - Automated Analysis and Reporting]
        I[Testing Framework
           - Test Keys with Known Patterns]
        J[Documentation
           - Analysis Guide & Mitigation Strategies]
    end

    A --> B
    B --> C
    B --> D
    D --> E
    D --> F
    D --> G
    E --> H
    F --> H
    G --> H
    H --> I
    I --> J
``` 