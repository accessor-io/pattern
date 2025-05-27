# Shor's Algorithm Implementation

This is an implementation of Shor's algorithm, a quantum algorithm for factoring integers in polynomial time. The algorithm is significant because it can break RSA encryption by efficiently factoring large numbers.

## Requirements

- Python 3.7+
- Qiskit (IBM's quantum computing SDK)
- NumPy
- Matplotlib (for visualization)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python shors_algorithm.py <integer_to_factor>
```

## How It Works

Shor's algorithm works by finding the period of a function, which can then be used to factor an integer. The algorithm has two parts:

1. A classical part that reduces factoring to finding the period of a function
2. A quantum part that efficiently finds the period using quantum parallelism

The algorithm's strength lies in its ability to perform quantum Fourier transform to find the period in O(log N) time versus classical algorithms that require O(N^(1/3)) time. 